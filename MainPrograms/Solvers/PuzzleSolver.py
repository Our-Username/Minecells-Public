from MainPrograms.Solvers.SpaceBoardLogicalSolver import SpaceBoardLogicalSolver

type Board = list[list[int]]
type TilePosition = tuple[int, int]


class PuzzleSolver(SpaceBoardLogicalSolver):
	def __init__(self, n_cols: int, n_rows: int, minecount: int) -> None:
		"""
			Constructor method for PuzzleSolver class

			Inputs:
				- n_cols: number of columns in the board
				- n_cols: number of rows in the board
				- start_pos: the tile the user clicks to start the game
				- minecount: the number of mines the user has to find
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
		
		super().__init__(n_cols, n_rows, (n_rows + 1, n_cols + 1), minecount)
		self._board: Board = [[-2 for _ in range(self._n_cols)] for _ in range(self._n_rows)]  #initialize other variables and objects
	
	def puzzle_solve(self, answer_board: Board, revealed_tiles: set[TilePosition], spaces: set[TilePosition] = None) -> tuple[Board, set[TilePosition], bool]:
		"""
			Runs the solvers repeatedly until either no more information is found (at which point it is unsolvable)
			or until the entire board is solved

			Inputs:
				- answer_board: the board generated that the solver checks against
			Outputs:
				- mines: the set of mines found
				- the set of tiles next to the border
				- bool: whether the board is solvable
		"""
		
		# initialize the test board. The start position is always 0
		test_board: list[list[int]] = [[-2 for _ in range(self._n_cols)] for _ in range(self._n_rows)]
		
		#initialize the spaces
		for row, col in spaces:
			test_board[row][col] = -3
		
		#initialize the revealed tiles
		start_safes: set[TilePosition] = set()
		for row, col in revealed_tiles:
			test_board[row][col] = answer_board[row][col]
			start_safes.add((row, col))
		
		# initialize these variables
		old_borders: set[TilePosition] = set()
		new_safes: set[TilePosition] = set(start_safes)
		mines = set()
		
		# while there is still a tile that is covered
		while self._check_for_covered_tile(test_board):
			
			# run logical solver
			new_mines, new_safes, old_borders = self._find_logical_progress(test_board, new_safes, old_borders)
			
			# if nothing found, run the matrix solver
			if not new_mines and not new_safes:
				new_mines, new_safes, old_borders = self._find_progress(test_board, new_safes, old_borders)
				
				# if nothing found, the board is unsolvable
				if not new_mines and not new_safes:
					return test_board, set(self._build_var_list(self._build_var_dict(old_borders, test_board))), False
			
			# update the safe tiles
			for row, col in new_safes:
				test_board[row][col] = answer_board[row][col]
			
			# update the mines
			for row, col in new_mines:
				test_board[row][col] = -1
				mines.add((row, col))
		
		# return results
		return test_board, set(), True
