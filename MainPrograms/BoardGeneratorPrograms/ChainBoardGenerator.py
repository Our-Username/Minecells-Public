from MainPrograms.BoardGeneratorPrograms.BoardGenerator import BoardGenerator
from MainPrograms.Solvers.ChainLogicalSolver import ChainLogicalSolver

type Board = list[list[int]]
type TilePosition = tuple[int, int]


class ChainBoardGenerator(BoardGenerator):
	def __init__(self, n_cols: int, n_rows: int, start_pos: TilePosition, minecount: int, seed: str, process_count: int = 0) -> None:
		"""
			Constructor method for ChainBoardGenerator class

			Inputs:
				- n_cols: number of columns in the board
				- n_rows: number of rows in the board
				- start_pos: the tile the user clicks to start the game
				- minecount: the number of mines the user has to find
				- seed: the seed used to generate the board. Default is "", which indicates that a random seed should be generated.
				- process_count: the number of simultaneous boards generated in parallel
			Initializes:
				- self._n_cols: number of columns in the board
				- self._n_rows: number of rows in the board
				- self._start_pos: the tile the user clicks to start the game
				- self._minecount: the number of mines the user has to find
				- self._seed: the seed used to generate the board. Default is "", which indicates that a random seed should be generated.
				- self.board: the board generated
				- self._directions: the positions relative to a tile of the adjacent tiles
				- self._solver: the solver used to check whether the given board is solvable
				- self._seed_gen: a seed generator object to be used by the board generator
				- self._mine_positions: the positions of all valid mines as a list
		"""
		super().__init__(n_cols, n_rows, start_pos, minecount, seed=seed, process_count=process_count)
		self._solver: ChainLogicalSolver = ChainLogicalSolver(n_cols=self._n_cols, n_rows=self._n_rows, minecount=self._minecount, start_pos=self._start_pos)
	
	def _generate_board(self) -> Board:
		"""
			Returns a board based on _mine_pos which is obtained through the seed class

			Inputs:
				- None
			Outputs:
				- target_board: the board generated
		"""
		# initialize mines to keep track of mines generated
		mines: set[TilePosition] = set()
		# initialize board
		target_board: Board = [[0 for _ in range(self._n_cols)] for _ in range(self._n_rows)]
		
		#make sure that the tiles around the start position are always safe
		safes: set[TilePosition] = set((row + self._start_pos[0], col + self._start_pos[1]) for row, col in self._directions)
		
		#store mine positions as a set locally to avoid recalculation
		mine_pos = set(self._mine_positions)
		
		# while not all mines placed
		while len(mines) < self._minecount:
			#set defaults
			mine_one: TilePosition = (-1, -1)
			mine_two: TilePosition = (-1, -1)
			mine_one_orth: set[TilePosition] = set()
			
			# store exclusions once to avoid recalculation
			exclusions = mines.union(safes)
			select_from = mine_pos - exclusions
			loc_safes = set()
			
			#while at least one mine has failed to place
			while mine_two == (-1, -1) or mine_one == (-1, -1):
				# store exclusions once to avoid recalculation
				loc_safes.add(mine_one)
				loc_safes.add(mine_two)
				
				#attempt to place both mines
				mine_one: TilePosition = self._seed_gen.give_random_tile(select_from=select_from - loc_safes)
				mine_one_orth = self._solver.get_orthogonal_adj(mine_one)  #avoid recalculation
				mine_two: TilePosition = self._seed_gen.give_random_tile(select_from=mine_one_orth - exclusions - loc_safes)
			
			#update the safe tile set with the local safe tiles
			safes.update(loc_safes)
			
			#set the two mine positions to mines
			mines.add(mine_one)
			target_board[mine_one[0]][mine_one[1]] = -1
			mines.add(mine_two)
			target_board[mine_two[0]][mine_two[1]] = -1
			
			#add their adjacent tiles to a set of safe tiles to reduce the positions of mines later on
			for position in mine_one_orth:
				safes.add(position)
			for position in self._solver.get_orthogonal_adj(mine_two):
				safes.add(position)
			
			#increment adjacent numbers as before
			for row, col in self._get_adjacent_tiles(mine_one):
				if target_board[row][col] >= 0:
					target_board[row][col] += 1
			for row, col in self._get_adjacent_tiles(mine_two):
				if target_board[row][col] >= 0:
					target_board[row][col] += 1
		
		return target_board
