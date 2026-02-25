from MainPrograms.Solvers.PuzzleSolver import PuzzleSolver

type Board = list[list[int]]
type TilePosition = tuple[int, int]


class OffsetPuzzleSolver(PuzzleSolver):
	def __init__(self, n_cols: int, n_rows: int, minecount: int, directions: list[TilePosition]) -> None:
		"""
			Constructor method for OffsetPuzzleSolver class

			Inputs:
				- n_cols: number of columns in the board
				- n_cols: number of rows in the board
				- start_pos: the tile the user clicks to start the game
				- minecount: the number of mines the user has to find
				- directions: the tiles to be treated as adjacent
			Initializes:
				- self._n_cols: number of columns in the board
				- self._n_rows: number of rows in the board
				- self._start_pos: the tile the user clicks to start the game
				- self._minecount: the number of mines the user has to find
				- self._seed: the seed used to generate the board. Default is "", which indicates that a random seed should be generated.
				- self.board: the board generated
				- self._solver: the solver used to check whether the given board is solvable
				- self._seed_gen: a seed generator object to be used by the board generator
				- self._mine_positions: the positions of all valid mines as a list
				- self._space_count: the number of empty (space) tiles to be generated
				- directions: the tiles to be treated as adjacent
		"""
		
		super().__init__(n_cols, n_rows, minecount)
		self._directions = directions
