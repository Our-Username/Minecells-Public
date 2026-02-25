from MainPrograms.Solvers.MatrixSolver import MatrixSolver

type Board = list[list[int]]
type TilePosition = tuple[int, int]


class SpaceBoardMatrixSolver(MatrixSolver):
	def __init__(self, n_cols: int, n_rows: int, start_pos: TilePosition, minecount: int) -> None:
		"""
			Constructor method for SpaceBoardLogicalSolver class

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
		"""
		
		super().__init__(n_cols=n_cols, n_rows=n_rows, start_pos=start_pos, minecount=minecount)
	
	def _covered_adjacent_tiles(self, pos: TilePosition, board: Board, mines: bool = False) -> set[TilePosition]:
		"""
			Gives the positions of the adjacent covered tiles

			Inputs:
				- pos: the target tile position
				- board: the board to work on
				- mines: return the tiles with flags as well as covered tiles
			Returns:
				- output_set: the list of adjacent covered tiles
		"""
		output_set: set[TilePosition] = set()  # initialise output set
		
		if not mines:  # if mines not requested
			for row, col in self._directions:  # for each adjacent tile
				rx, ry = pos[0] + row, pos[1] + col
				if 0 <= rx < self._n_rows and 0 <= ry < self._n_cols:  # if tile is within board
					if board[rx][ry] == -2:  # if tile is covered
						output_set.add((rx, ry))
		else:  # if mines requested
			for row, col in self._directions:  # for each adjacent tile
				rx, ry = pos[0] + row, pos[1] + col
				if 0 <= rx < self._n_rows and 0 <= ry < self._n_cols:  # if tile is within board
					if board[rx][ry] in [-1, -2]:  # if tile is flagged or covered
						output_set.add((rx, ry))
		
		return output_set