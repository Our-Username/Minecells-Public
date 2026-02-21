from MainPrograms.Solvers.MatrixSolver import MatrixSolver

type Board = list[list[int]]
type Matrix = list[list[float]]
type TilePosition = tuple[int, int]


class ChainMatrixSolver(MatrixSolver):
	def __init__(self, n_cols: int, n_rows: int, start_pos: TilePosition, minecount: int) -> None:
		"""
			Constructor method for MatrixSolver class

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
				- self._orthogonal_directions: the positions relative to a tile of the orthogonally adjacent tiles
		"""
		super().__init__(n_cols=n_cols, n_rows=n_rows, start_pos=start_pos, minecount=minecount)
		
		# directions of orthogonal tiles
		self._orthogonal_directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
	
	def _get_covered_orthogonal_adj(self, pos: TilePosition, board: Board) -> set[TilePosition]:
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
			
			# store to local variable to avoid recalculating
			target_row, target_col = pos[0] + row, pos[1] + col
			
			# if position within the board
			if 0 <= target_row < self._n_rows and 0 <= target_col < self._n_cols:
				#if position is covered
				if board[target_row][target_col] == -2:
					# add it to the set
					output_set.add((target_row, target_col))
		
		return output_set
	
	def _build_var_dict_chain(self, border_tiles: set[TilePosition], mines: set[TilePosition], answer_board: Board) -> dict[TilePosition:list[TilePosition]]:
		"""
			Creates an adjacency dictionary, indicating each tiles on the border, and the positions of adjacent unchecked tiles.

			Inputs:
				- border_clues: a list of all the positions of tiles that are on the border (see get_borders)
				- mines: the list of unpaired mines
				- board: the board to run the check on
			Returns:
				- output_dict: a dictionary in the form {tile: set(adjacent tiles)}
		"""
		
		#for each border tile
		output_dict: dict[TilePosition:list[TilePosition]] = {}
		for pos in border_tiles:
			output_dict[pos] = self._covered_adjacent_tiles(pos, answer_board)
		
		#for each unpaired mine
		for pos in mines:
			output_dict[pos] = self._get_covered_orthogonal_adj(pos, answer_board)
		
		return output_dict
	
	def _build_mat_chain(self, var_dict: dict[TilePosition:list[TilePosition]], var_list: list[TilePosition], board: Board) -> Matrix:
		"""
			Builds the matrix to be analysed

			Inputs:
				- var_dict: a dictionary that relates the "result" with adjacent position
				- var_list: a list of all covered "variables"
			Outputs:
				- mat: the matrix to analyse
		"""
		# initialize the matrix
		mat: Matrix = []
		
		# for each row
		for result_tile in var_dict.keys():
			
			# initialize a row
			row: list[int] = []
			
			# for each variable
			for pos in var_list:
				
				# if adjacent to the result tile, its coefficient is 1, else 0
				if pos in var_dict[result_tile]:
					row.append(1)
				else:
					row.append(0)
			
			# add the row to the matrix, with the result
			if board[result_tile[0]][result_tile[1]] >= 0:
				row.append(self.get_effective_num(result_tile, board))
			else:
				row.append(1)
			mat.append(row)
		
		# minecount
		# if all remaining tiles are adjacent to the borders
		if self._get_covered_tiles(board) == set(var_list) and len(var_list) != 0:
			row: list[int] = []
			
			# create a final row with all 1s that must add up to the minecount
			for _ in range(len(var_list)):
				row.append(1)
			row.append(self._get_current_minecount(board))
			mat.append(row)
		
		return mat
	
	def _find_progress_chain(self, answer_board: Board, new_safe_set: set[TilePosition], old_borders: set[TilePosition], mines: set[TilePosition]) -> tuple[set[TilePosition], set[TilePosition], set[TilePosition]]:
		"""
			Runs the matrix generators and analysers.

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
		
		# get information for matrix building
		var_dict: dict[TilePosition:list[TilePosition]] = self._build_var_dict_chain(borders, mines, answer_board)
		var_list: list[TilePosition] = self._build_var_list(var_dict)
		
		# build the matrix
		mat: Matrix = self._build_mat_chain(var_dict, var_list, answer_board)
		
		# conduct Gaussian elimination to make the matrix easier to solve
		new_mat: Matrix = self._row_echelon(mat)
		
		# get the positions of all the mine and safe tiles from the matrix
		mines, safes = self._analyse_matrix(new_mat, var_list)
		
		# return results.
		return mines, safes, borders