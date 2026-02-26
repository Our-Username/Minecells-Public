from MainPrograms.BoardGeneratorPrograms.SpaceBoardGenerator import SpaceBoardGenerator
from MainPrograms.Solvers.PuzzleSolver import PuzzleSolver
import copy
from multiprocessing import Event

type Board = list[list[int]]
type TilePosition = tuple[int, int]


class PuzzleBoardGenerator(SpaceBoardGenerator):
	def __init__(self, n_cols: int, n_rows: int, minecount: int, seed: str, space_count: int, difficulty: int, process_count: int = 0) -> None:
		"""
			Constructor method for PuzzleBoardGenerator class

			Inputs:
				- n_cols: number of columns in the board
				- n_rows: number of rows in the board
				- minecount: the number of mines the user has to find
				- seed: the seed used to generate the board. Default is "", which indicates that a random seed should be generated.
				- space_count: the number of empty (space) tiles to be generated
				- difficulty: a modifier used to help control the amount of revealed tiles are generated
				- process_count: the number of simultaneous boards generated in parallel
			Initializes:
				- self._n_cols: number of columns in the board
				- self._n_rows: number of rows in the board
				- self._minecount: the number of mines the user has to find
				- self._seed: the seed used to generate the board. Default is "", which indicates that a random seed should be generated.
				- self.board: the board generated
				- self._directions: the positions relative to a tile of the adjacent tiles
				- self._solver: the solver used to check whether the given board is solvable
				- self._seed_gen: a seed generator object to be used by the board generator
				- self._mine_positions: the positions of all valid mines as a list
				- self._space_count: the number of empty (space) tiles to be generated
				- self._difficulty: a modifier used to help control the amount of revealed tiles are generated
		"""
		
		super().__init__(n_cols, n_rows, (n_rows + 5, n_cols + 5), minecount, seed, space_count, process_count=process_count)
		self._solver: PuzzleSolver = PuzzleSolver(n_cols, n_rows, minecount)
		self._difficulty: int = difficulty
	
	def _generate_board_puzzle(self, space_positions: set[TilePosition] = None) -> tuple[Board, set[TilePosition], set[TilePosition]]:
		"""
			Returns a board based on _mine_pos which is obtained through the seed class

			Inputs:
				- space_positions: the positions of all spaces that need to be carried forwards to the next iteration
			Outputs:
				- target_board: the board generated
				- mines: the positions of all mines generated
				- spaces: the positions of all empty tiles
		"""
		# initialize mines to keep track of mines generated
		mines: set[TilePosition] = set()
		# initialize board
		target_board: Board = [[0 for _ in range(self._n_cols)] for _ in range(self._n_rows)]
		
		index = 0
		while len(mines) < self._minecount:  # while not all mines placed
			current_mine: TilePosition = self._mine_positions[index]
			if target_board[current_mine[0]][current_mine[1]] != -1:  # if mine not already placed
				mines.add(current_mine)  # place mine
				target_board[current_mine[0]][current_mine[1]] = -1
				
				for row, col in self._get_adjacent_tiles(current_mine):  # update all numbers
					if target_board[row][col] != -1:  # exclude mines to not overwrite them
						target_board[row][col] += 1
			index += 1  # look at next position
		
		#get a list of valid positions for space tiles
		space_positions = self._seed_gen.generate_mines_list(includes=space_positions, excludes=mines)
		spaces: set[TilePosition] = set()
		index = 0
		
		while len(spaces) < self._space_count:  # while not all spaces placed
			current_space = space_positions[index]
			if target_board[current_space[0]][current_space[1]] >= 0:  # if space not already placed
				spaces.add(current_space)  # place space
				target_board[current_space[0]][current_space[1]] = -3
			index += 1  # look at next position
		
		return target_board, mines, spaces
	
	def _add_tile(self,
				  repetitions: int,
				  tiles_required: int,
				  new_positions: set[TilePosition],
				  revealed_tiles: set[TilePosition],
				  mines: set[TilePosition],
				  spaces: set[TilePosition],
				  always_exclude: set[TilePosition]) -> set[TilePosition]:
		"""
			Adds a tile or group of tiles to the set of revealed tiles
			
			Inputs:
				- repetitions: the amount of tiles to add
				- tiles_required: the absolute limit of revealed tiles before a reset
				- new_positions: the default set of tiles to select from
				- revealed_tiles: the previous set of revealed tiles
				- mines: the set of all placed mines
				- spaces: the set of all placed empty tiles
				- always exclude: the set of all tiles on the edge of the board
			Outputs:
				- revealed_tiles: the new set of revealed tiles
			
		"""
		# reveal multiple tiles at once to reduce the amount of solves the solver has to make
		exclusions = revealed_tiles.union(mines, always_exclude, spaces, *(self._get_adjacent_tiles(pos) for pos in revealed_tiles))
		
		#create deep copies of these parameters to ensure that they don't affect the variables outside the function
		local_new_positions = copy.deepcopy(new_positions)
		local_revealed_tiles = copy.deepcopy(revealed_tiles)
		
		for _ in range(repetitions):
			
			# if new_positions is empty (ie there is an island), get a random valid tile from anywhere in the board
			if not (local_new_positions - local_revealed_tiles):
				new_tile = self._seed_gen.give_random_tile(excludes=exclusions)
				if new_tile != (-1, -1):
					local_new_positions.add(new_tile)
			
			# Remove invalid tiles from the valid set
			valid_positions = local_new_positions - exclusions - local_revealed_tiles
			
			# do a full reset if all new_positions are on the edge
			new_valid_positions = (local_new_positions - always_exclude - mines - spaces - local_revealed_tiles)
			if not new_valid_positions:
				return set((a, a) for a in range(tiles_required + 1))
			
			# add the generated tile to the set of revealed tiles
			if valid_positions:
				local_revealed_tiles.add(self._seed_gen.give_random_tile(select_from=valid_positions))
			else:
				local_revealed_tiles.add(self._seed_gen.give_random_tile(select_from=new_valid_positions))
			
			# add that tile to the excluded tiles to make sure that the same tile cannot be added more than once
			exclusions.update(local_revealed_tiles)
		return local_revealed_tiles
	
	def generate_no_guess_board(self) -> set[TilePosition]:
		"""
			Modifies self.board to generate a board.

			Inputs:
				- None
			Modifies:
				- self.board: the board generated
		"""
		
		# initialize variables
		solvable: bool = False
		revealed_tiles: set[TilePosition] = set()
		new_positions: set[TilePosition] = set()
		mines: set[TilePosition]
		spaces: set[TilePosition]
		
		# generate a board to test
		self._board, mines, spaces = self._generate_board_puzzle(set())
		
		# store board area and revealed tiles requirement to simplify future calculations
		area = self._n_cols * self._n_rows
		tiles_required: int = min(len(str((self._difficulty + 1) * area)) * self._difficulty, area // 5)
		
		# control how many tiles are revealed each iteration
		if tiles_required == area // 5:
			repetitions = 1
		else:
			repetitions = self._difficulty
		
		# exclude these tiles to ensure that a tile in the middle is always the one being revealed
		always_exclude: set[TilePosition] = set((0, col) for col in range(self._n_cols))
		always_exclude.update(set((self._n_rows - 1, col) for col in range(self._n_cols)))
		always_exclude.update((row, 0) for row in range(self._n_rows))
		always_exclude.update((row, self._n_cols - 1) for row in range(self._n_rows))
		
		# loop until a solvable board is found
		while not solvable:
			# if too many spaces are revealed
			if len(revealed_tiles) >= tiles_required:
				# reset the board
				self._reset_board(set())
				revealed_tiles = set()
				
				# generate a board to test
				self._board, mines, spaces = self._generate_board_puzzle(set())
				
				new_positions = {self._seed_gen.give_random_tile(excludes=always_exclude.union(mines, spaces))}
			
			while len(revealed_tiles) < tiles_required:
				revealed_tiles = self._add_tile(repetitions, tiles_required, new_positions, revealed_tiles, mines, spaces, always_exclude)
			
			# if there are no more valid positions, do a full reset and skip solving
			if len(revealed_tiles) > tiles_required:
				continue
			
			# solve the board, and keep track of solved mines
			_, new_positions, solvable = self._solver.puzzle_solve(self._board, revealed_tiles, spaces)
		
		# reveal more tiles to make the board easier
		while len(revealed_tiles) < tiles_required:
			exclusions = revealed_tiles.union(mines, always_exclude, spaces)
			revealed_tiles.add(self._seed_gen.give_random_tile(excludes=exclusions))
		
		return revealed_tiles
	
	def generate_no_guess_board_parallel(self, start_event: Event) -> set[TilePosition] | None:
		"""
			Modifies self.board to generate a board.

			Inputs:
				- None
			Modifies:
				- self.board: the board generated
		"""
		
		# initialize variables
		revealed_tiles: set[TilePosition] = set()
		new_positions: set[TilePosition] = set()
		mines: set[TilePosition]
		spaces: set[TilePosition]
		
		# generate a board to test
		self._board, mines, spaces = self._generate_board_puzzle(set())
		
		# store board area and revealed tiles requirement to simplify future calculations
		area = self._n_cols * self._n_rows
		tiles_required: int = min(len(str((self._difficulty + 1) * area)) * self._difficulty, area // 5)
		
		# control how many tiles are revealed each iteration
		if tiles_required == area // 5:
			repetitions = 1
		else:
			repetitions = self._difficulty
		
		# exclude these tiles to ensure that a tile in the middle is always the one being revealed
		always_exclude: set[TilePosition] = set((0, col) for col in range(self._n_cols))
		always_exclude.update(set((self._n_rows - 1, col) for col in range(self._n_cols)))
		always_exclude.update((row, 0) for row in range(self._n_rows))
		always_exclude.update((row, self._n_cols - 1) for row in range(self._n_rows))
		
		# loop until a solvable board is found
		while not start_event.is_set():
			# if too many spaces are revealed
			if len(revealed_tiles) >= tiles_required:
				# reset the board
				self._reset_board(set())
				revealed_tiles = set()
				
				# generate a board to test
				self._board, mines, spaces = self._generate_board_puzzle(set())
				
				new_positions = {self._seed_gen.give_random_tile(excludes=always_exclude.union(mines, spaces))}
			
			#until there are enough new tiles, add a new revealed tile to the set
			while len(revealed_tiles) < tiles_required:
				revealed_tiles = self._add_tile(repetitions, tiles_required, new_positions, revealed_tiles, mines, spaces, always_exclude)
			
			# if there are no more valid positions, do a full reset and skip solving
			if len(revealed_tiles) > tiles_required:
				continue
			
			# solve the board, and keep track of solved mines
			_, new_positions, solvable = self._solver.puzzle_solve(self._board, revealed_tiles, spaces)
			
			#terminate the process early if another process finds a board first
			if start_event.is_set():
				return None
			
			#if solvable
			if solvable:
				
				#if not other process has finished
				if not start_event.is_set():
					# reveal more tiles to make the board easier
					while len(revealed_tiles) < tiles_required:
						exclusions = revealed_tiles.union(mines, always_exclude, spaces)
						revealed_tiles.add(self._seed_gen.give_random_tile(excludes=exclusions))
					
					#indicate to the other processes that a board has been found
					start_event.set()
				break
		
		return revealed_tiles
