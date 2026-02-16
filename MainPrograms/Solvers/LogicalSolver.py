from MainPrograms.Solvers.MatrixSolver import MatrixSolver

type Board = list[list[int]]
type Matrix = list[list[float]]
type TilePosition = tuple[int, int]


class LogicalSolver(MatrixSolver):
	def __init__(self, n_cols: int, n_rows: int, start_pos: TilePosition, minecount: int) -> None:
		"""
			Constructor method for LogicalSolver class

			Inputs:
				- n_cols: number of columns in the board
				- n_cols: number of rows in the board
				- start_pos: the tile the user clicks to start the game
				- minecount: the number of mines the user has to find
			Initializes:
				- self._n_cols: number of columns in the board
				- self._n_cols: number of rows in the board
				- self._start_pos: the tile the user clicks to start the game
				- self._minecount: the number of mines the user has to find
				- self._directions: the positions relative to a tile of the adjacent tiles
				- self._directions: the positions relative to a tile of the adjacent tiles
				- self._orthogonal_directions: the positions relative to a tile of the orthogonally adjacent tiles
		"""
		
		super().__init__(n_cols=n_cols, n_rows=n_rows, start_pos=start_pos, minecount=minecount)
		
		# directions of orthogonal tiles
		self._orthogonal_directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
	
	def _get_adjacent_tiles(self, pos: TilePosition) -> set[TilePosition]:
		"""
			Gives the positions of the adjacent tiles

			Inputs:
				- pos: the target tile position
			Returns:
				- output_set: the list of adjacent tiles
		"""
		output_set: set[TilePosition] = set()  # initialise output set
		
		for i, j in self._directions:  # for each adjacent tile
			if 0 <= pos[0] + i < self._n_rows and 0 <= pos[1] + j < self._n_cols:  # if position within the board
				output_set.add((pos[0] + i, pos[1] + j))  # add it to the set
		
		return output_set
	
	def get_orthogonal_adj(self, pos: TilePosition):
		"""
			Gives the positions of the orthogonally adjacent tiles

			Inputs:
				- pos: the target tile position
			Returns:
				- output_set: the list of orthogonally adjacent tiles
		"""
		
		# initialise output set
		output_set: set[TilePosition] = set()
		
		# for each orthogonally adjacent tile
		for row, col in self._orthogonal_directions:
			
			#store to local variable to avoid recalculating
			target_row, target_col = pos[0] + row, pos[1] + col
			
			# if position within the board
			if 0 <= target_row < self._n_rows and 0 <= target_col < self._n_cols:
				# add it to the set
				output_set.add((target_row, target_col))
		
		return output_set
	
	def _check_resolved_tile(self, borders: set[TilePosition], board: Board) -> tuple[set[TilePosition], set[TilePosition]]:
		"""
			Checks if the solution around a tile is trivial, ie if all the mines or all the safe spaces are found
			
			Inputs:
				- borders: the set of tiles on the border. These tiles give all the information needed
				- board: the board to check
			Outputs:
				- mines: the set of all discovered mines
				- safes: the set of all discovered safe tiles
		"""
		
		#initialize mines and safes
		mines: set[TilePosition] = set()
		safes: set[TilePosition] = set()
		temp_board: Board = [row[:] for row in board]
		
		#for each tile
		for row, col in borders:
			
			#get the positions of all covered tiles (including mines) that are adjacent
			spaces = self._covered_adjacent_tiles((row, col), temp_board, True)
			
			#if the number of adjacent covered tiles (including mines) equals the number displayed
			if len(spaces) == temp_board[row][col]:
				
				#all the adjacent tiles must be mines
				for target_row, target_col in spaces:
					mines.add((target_row, target_col))
					temp_board[target_row][target_col] = -1
			
			#if the numbers of mines that are adjacent equals the number displayed
			elif sum(1 for target_row, target_col in spaces if temp_board[target_row][target_col] == -1) == temp_board[row][col]:
				
				#all the adjacent unflagged tiles must be safes
				for target_row, target_col in spaces:
					if temp_board[target_row][target_col] == -2:
						safes.add((target_row, target_col))
						temp_board[target_row][target_col] = 0
		
		#return results
		return mines, safes
	
	def _check_one_two_pattern(self, borders: set[TilePosition], board: Board) -> tuple[set[TilePosition], set[TilePosition]]:
		"""
			Checks for the presence of a one-two pattern.

			Inputs:
				- borders: the set of tiles on the border. These tiles give all the information needed
				- board: the board to check
			Outputs:
				- mines: the set of all discovered mines
				- safes: the set of all discovered safe tiles
		"""
		
		# initialize mines and safes
		mines: set[TilePosition] = set()
		safes: set[TilePosition] = set()
		
		# for each tile
		for border_position in borders:
			
			#if the current number is not 2, skip this tile
			if self.get_effective_num(border_position, board) != 2:
				continue
			
			#for each orthogonally adjacent tile
			for target_position in self.get_orthogonal_adj(border_position):
				
				#if tile is not a border tile, skip this tile
				if target_position not in borders:
					continue
				
				# if tile is not 1, skip this tile
				if self.get_effective_num(target_position, board) != 1:
					continue
				
				#get the sets of tiles that are directly adjacent to the two tiles
				border_adjacent_tiles_set: set[TilePosition] = self._covered_adjacent_tiles(border_position, board, False)
				target_adjacent_tiles_set: set[TilePosition] = self._covered_adjacent_tiles(target_position, board, False)
				
				#get the set of tiles that are shared between the two target tiles
				shared_tiles_set: set[TilePosition] = border_adjacent_tiles_set & target_adjacent_tiles_set
				
				#if all tiles but one are shared between the shared tiles and the tiles adjacent to the "2" border tile, that tile must be a mine
				if len(border_adjacent_tiles_set) - len(shared_tiles_set) == 1:
					mines.update(border_adjacent_tiles_set - shared_tiles_set)
					
					#if any tiles are shared between the shared tiles and the tiles adjacent to the "1" border tile, those tiles must be safe
					safes.update(target_adjacent_tiles_set - shared_tiles_set)
		
		#return results
		return mines, safes
	
	def _find_logical_progress(self, answer_board: Board, new_safe_set: set[TilePosition], old_borders: set[TilePosition]) -> tuple[set[TilePosition], set[TilePosition], set[TilePosition]]:
		"""
			Runs the pattern recognition algorithms

			Inputs:
				- answer_board: the board to run the check on
				- new_safe_set: the set of all tiles that were found to be safe in the last iteration
				- old_borders: the set of all tiles that were borders in the last iteration
			Returns:
				- mines: the set of tiles that are guaranteed to be mines
				- safes: the set of tiles that are guaranteed to be safes
				- borders: the set of border tiles
		"""
		
		# get the position of all the border tiles
		borders: set[TilePosition] = self.get_border_tiles(answer_board, new_safe_set, old_borders)
		
		# if there aren't any (ie they are all surrounded by flags, the board is unsolvable
		if not borders:
			return set(), set(), set()
		
		#get mines and safes from resolved tiles
		new_mines, new_safes = self._check_one_two_pattern(borders, answer_board)
		mines, safes = self._check_resolved_tile(borders, answer_board)
		
		mines.update(new_mines)
		safes.update(new_safes)
		
		#return results
		return mines, safes, borders
	
	@staticmethod
	def _check_for_covered_tile(board: Board) -> bool:
		"""
			Checks whether there is at least one tile on the board that is still covered.

			Inputs:
				- board: the board to be checked against
			Outputs:
				- bool: whether there is still a covered tile on the board
		"""
		
		# return false if there are no covered tiles left
		return any(-2 in row for row in board)
	
	def solve(self, answer_board: Board) -> tuple[set[TilePosition], bool]:
		"""
			Runs the solvers repeatedly until either no more information is found (at which point it is unsolvable)
			or until the entire board is solved
			
			Inputs:
				- answer_board: the board generated that the solver checks against
			Outputs:
				- mines: the set of mines found
				- safes: the set of safe tiles found
				- bool: whether the board is solvable
		"""
		
		#initialize the test board. The start position is always 0
		test_board: list[list[int]] = [[-2 for _ in range(self._n_cols)] for _ in range(self._n_rows)]
		test_board[self._start_pos[0]][self._start_pos[1]] = 0
		
		#resolve first iteration. The tiles around the start position are always safe
		start_adjacency: set[TilePosition] = self._get_adjacent_tiles(self._start_pos)
		start_adjacency.add(self._start_pos)
		for row, col in start_adjacency:
			test_board[row][col] = answer_board[row][col]
		
		#initialize these variables
		old_borders: set = set().union({self._start_pos})
		new_safes: set = set(start_adjacency)
		mines = set()
		
		#while there is still a tile that is covered
		while self._check_for_covered_tile(test_board):
			
			#run logical solver
			new_mines, new_safes, old_borders = self._find_logical_progress(test_board, new_safes, old_borders)
			
			#if nothing found, run the matrix solver
			if not new_mines and not new_safes:
				new_mines, new_safes, old_borders = self._find_progress(test_board, new_safes, old_borders)
				
				# if nothing found, the board is unsolvable
				if not new_mines and not new_safes:
					return mines, False
			
			#update the safe tiles
			for row, col in new_safes:
				test_board[row][col] = answer_board[row][col]
			
			# update the mines
			for row, col in new_mines:
				test_board[row][col] = -1
				mines.add((row, col))
		
		#return results
		return set(), True