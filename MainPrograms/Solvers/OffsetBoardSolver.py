from MainPrograms.Solvers.SpaceBoardLogicalSolver import SpaceBoardLogicalSolver

type Board = list[list[int]]
type TilePosition = tuple[int, int]


class OffsetBoardSolver(SpaceBoardLogicalSolver):
	def __init__(self, n_cols: int, n_rows: int, start_pos: TilePosition, minecount: int, directions: list[TilePosition]) -> None:
		"""
			Constructor method for OffsetBoardSolver class

			Inputs:
				- n_cols: number of columns in the board
				- n_cols: number of rows in the board
				- start_pos: the tile the user clicks to start the game
				- minecount: the number of mines the user has to find
				- directions: the tiles to be treated as adjacent
			Initializes:
				- self._n_cols: number of columns in the board
				- self._n_cols: number of rows in the board
				- self._start_pos: the tile the user clicks to start the game
				- self._minecount: the number of mines the user has to find
				- self._directions: the positions relative to a tile of the adjacent tiles
		"""
		
		super().__init__(n_cols, n_rows, start_pos, minecount)
		self._directions = directions
	
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
		
		# if there aren't any (ie they are all surrounded by flags), the board is unsolvable
		if not borders:
			return set(), set(), set()
		
		# get mines and safes from resolved tiles
		mines, safes = self._check_resolved_tile(borders, answer_board)
		
		# return results
		return mines, safes, borders
