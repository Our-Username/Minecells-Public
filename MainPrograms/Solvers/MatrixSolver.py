type Board = list[list[int]]
type Matrix = list[list[float]]
type TilePosition = tuple[int, int]


class MatrixSolver:
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
		"""
		self._n_cols: int = n_cols  # initialize variables from parameters
		self._n_rows: int = n_rows
		self._start_pos: TilePosition = start_pos
		self._minecount: int = minecount
		
		self._directions: list[TilePosition] = [(x, y) for x in [-1, 0, 1] for y in [-1, 0, 1]]
		
		self._directions.remove((0, 0))  # does not include itself
	
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
		
		if not mines:  #if mines not requested
			for row, col in self._directions:  #for each adjacent tile
				rx, ry = pos[0] + row, pos[1] + col
				if 0 <= rx < self._n_rows and 0 <= ry < self._n_cols:  #if tile is within board
					if board[rx][ry] == -2:  #if tile is covered
						output_set.add((rx, ry))
		else:  #if mines requested
			for row, col in self._directions:  #for each adjacent tile
				rx, ry = pos[0] + row, pos[1] + col
				if 0 <= rx < self._n_rows and 0 <= ry < self._n_cols:  #if tile is within board
					if board[rx][ry] < 0:  #if tile is flagged or covered
						output_set.add((rx, ry))
		
		return output_set
	
	def _get_adjacent_mines(self, position: TilePosition, board: Board) -> set[TilePosition]:
		"""
			Gives the positions of the adjacent covered tiles

			Inputs:
				- pos: the target tile position
				- board: the board to work on
			Returns:
				- output_set: the list of adjacent flagged mines
		"""
		output_set: set[TilePosition] = set()  # initialise output set
		
		for row, col in self._directions:  # for each adjacent tile
			rx, ry = (position[0] + row), (position[1] + col)
			if 0 <= rx < self._n_rows and 0 <= ry < self._n_cols:  # if tile is within board
				if board[rx][ry] == -1:  # if tile is flagged
					output_set.add((rx, ry))
		return output_set
	
	def _check_neighbour_covered(self, pos: TilePosition, board: Board) -> bool:
		"""
			Checks if at least one of the adjacent tiles to the given position is covered

			Inputs:
				- pos: the target tile position
				- board: the board to check for covered tiles on
			Returns:
				- output_set: the list of adjacent tiles
		"""
		for row, col in self._directions:  #for each neighbour
			target_x, target_y = (pos[0] + row), (pos[1] + col)
			if 0 <= target_x < self._n_rows and 0 <= target_y < self._n_cols:  #if within the board (range check)
				if board[target_x][target_y] == -2:  #if covered
					return True
		
		return False
	
	def get_effective_num(self, pos: TilePosition, board: Board) -> int:
		"""
			Gives the value of the given position - the number of flagged adjacent mines

			Inputs:
				- position: the target tile position
				- board: the board to check for unchecked tiles
			Returns:
				- the number of the tile at that position take away the number of discovered adjacent mines
		"""
		return board[pos[0]][pos[1]] - len(self._get_adjacent_mines(pos, board))
	
	def get_border_tiles(self, board: Board, new_safe_set: set[TilePosition], old_borders: set[TilePosition]) -> set[TilePosition]:
		"""
			Gets the positions of all tiles on the "border". This means that it is an uncovered tile that is adjacent to at least one covered tile

			Inputs:
				- board: the board to check for covered tiles on
				- new_safe_list: the list of tiles that have been discovered to be safe between last iteration and this iteration
				- old_borders: the set of tiles that were borders last iteration
			Returns:
				- output_set: the set of border tiles
		"""
		o_remove: set = set()  #initialize change sets
		o_add: set = set()
		
		for pos in old_borders:  #for each old border
			if not self._check_neighbour_covered(pos, board):  #if not a border anymore, remove it
				o_remove.add(pos)
		for pos in new_safe_set:
			if self._check_neighbour_covered(pos, board):  #if now a border, add it
				o_add.add(pos)
		
		return old_borders.union(o_add) - o_remove  #the set of border tiles
	
	def _get_covered_tiles(self, board: Board) -> set[TilePosition]:
		"""
			Gives the positions of all covered tiles

			Inputs:
				- board: the board to work on
			Returns:
				- output_set: the set of covered tiles
		"""
		output_set: set[TilePosition] = set()  # initialise output set
		
		for row in range(self._n_rows):
			for col in range(self._n_cols):  #for each tile
				if board[row][col] == -2:  #if tile is covered, add it to the set
					output_set.add((row, col))
		
		return output_set
	
	def _get_current_minecount(self, board: Board) -> int:
		"""
			Gets the current minecount as it would be displayed to the user

			Inputs:
				- board: the board to work on
			Returns:
				- count: the current minecount
		"""
		count = self._minecount  #initialize minecount
		
		for col in range(self._n_cols):
			for row in range(self._n_rows):  #for each tile
				if board[row][col] == -1:  #if tile is flag, decrement minecount
					count -= 1
		
		return count
	
	def _build_var_dict(self, border_tiles: set[TilePosition], answer_board: Board) -> dict[TilePosition:list[TilePosition]]:
		"""
			Creates an adjacency dictionary, indicating each tiles on the border, and the positions of adjacent unchecked tiles.

			Inputs:
				- border_clues: a list of all the positions of tiles that are on the border (see get_borders)
				- board: the board to run the check on
			Returns:
				- output_dict: a dictionary in the form {tile: set(adjacent tiles)}
		"""
		output_dict: dict[TilePosition:list[TilePosition]] = {}
		for pos in border_tiles:
			output_dict[pos] = self._covered_adjacent_tiles(pos, answer_board)
		
		return output_dict
	
	@staticmethod
	def _build_var_list(var_dict: dict[TilePosition:list[TilePosition]]) -> list[TilePosition]:
		"""
			Builds the matrix to be analysed

			Inputs:
				- var_dict: a dictionary that relates the "result" with adjacent position
			Outputs:
				- output_list: a list of all covered "variables"
		"""
		output_list: list[TilePosition] = []
		
		for target_pos in var_dict.keys():  #for each "result" variable
			for item in var_dict[target_pos]:  #for each item adjacent to that variable
				if item not in output_list:  #ensures uniqueness
					output_list.append(item)
		
		return output_list
	
	def _build_mat(self, var_dict: dict[TilePosition:list[TilePosition]], var_list: list[TilePosition], board: Board) -> Matrix:
		"""
			Builds the matrix to be analysed
			
			Inputs:
				- var_dict: a dictionary that relates the "result" with adjacent position
				- var_list: a list of all covered "variables"
			Outputs:
				- mat: the matrix to analyse
		"""
		#initialize the matrix
		mat: Matrix = []
		
		#for each row
		for result_tile in var_dict.keys():
			
			#initialize a row
			row: list[int] = []
			
			#for each variable
			for pos in var_list:
				
				#if adjacent to the result tile, its coefficient is 1, else 0
				if pos in var_dict[result_tile]:
					row.append(1)
				else:
					row.append(0)
			
			#add the row to the matrix, with the result
			row.append(self.get_effective_num(result_tile, board))
			mat.append(row)
		
		#minecount
		#if all remaining tiles are adjacent to the borders
		if self._get_covered_tiles(board) == set(var_list) and len(var_list) != 0:
			row: list[int] = []
			
			#create a final row with all 1s that must add up to the minecount
			for _ in range(len(var_list)):
				row.append(1)
			row.append(self._get_current_minecount(board))
			mat.append(row)
		
		return mat
	
	@staticmethod
	def _row_echelon(mat: Matrix) -> Matrix:
		"""
			Convert a matrix into row-echelon form.
			
			Inputs:
				- mat: The matrix to convert to row-echelon form
			Returns:
				- local_mat: The converted matrix
		"""
		local_mat = mat  #create a local copy to work on.
		rows: int = len(local_mat)  #get the size of the matrix
		cols: int = len(local_mat[0])
		
		target_row_index: int = 0  #work in it row by row, starting with the first row
		
		#Forwards gaussian elimination
		for target_column in range(cols - 1):  #for each column
			
			#Swapping step
			#find the row with the highest digit at the target column
			max_row = max(local_mat[target_row_index:], key=lambda param: abs(param[target_column]))
			
			# get the index of this row.
			max_index: int = local_mat.index(max_row)
			
			local_mat[max_index], local_mat[target_row_index] = local_mat[target_row_index], local_mat[max_index]  #swap the max row and the target row
			if local_mat[target_row_index][target_column] == 0:  #if the number in new target row at the target column is 0 anyway, skip it
				continue
			
			#Elimination step
			for row in range(target_row_index + 1, rows):  #for each row below the target row
				#factor to ensure that the number at that column always cancels to 0
				division_factor: float = local_mat[row][target_column] / local_mat[target_row_index][target_column]
				if not division_factor:  #if the factor is 0, it does nothing so continue to save time
					continue
				
				for col in range(target_column, cols):  #eliminate
					local_mat[row][col] -= local_mat[target_row_index][col] * division_factor
					
					if int(local_mat[row][col]) == local_mat[row][col]:  #purely for aesthetics, converts floats to ints if it doesn't affect the number
						local_mat[row][col] = int(local_mat[row][col])
			
			#if eliminated move onto the next row. This makes it increment both row and column
			target_row_index += 1
			if target_row_index >= rows - 1:  #if at the last row, finish
				break
		
		#Backwards gaussian elimination
		target_row_index: int = rows - 1
		for target_column in range(cols - 2, -1, -1):  # for each column, reversed
			if local_mat[target_row_index][target_column] == 0:  # if the number in new target row at the target column is 0 anyway, skip it
				continue
			
			# Elimination step
			for row in range(target_row_index - 1, - 1, -1):  # for each row above the target row
				
				# factor to ensure that the number at that column always cancels to 0
				division_factor: float = local_mat[row][target_column] / local_mat[target_row_index][target_column]
				
				# if the factor is 0, it does nothing so continue to save time
				if not division_factor:
					continue
				
				# Eliminate
				# All columns need to be considered this time, as all columns may have non-0 values
				for col in range(cols):
					local_mat[row][col] -= local_mat[target_row_index][col] * division_factor
					
					if int(local_mat[row][col]) == local_mat[row][col]:  # purely for aesthetics, converts floats to ints if it doesn't affect the number
						local_mat[row][col] = int(local_mat[row][col])
			
			# if eliminated move onto the next row. This makes it decrement both row and column
			target_row_index -= 1
			if target_row_index <= 0:  # if at the last row, finish
				break
		
		return local_mat
	
	@staticmethod
	def _analyse_matrix(mat: Matrix, var_list: list[TilePosition]) -> tuple[set[TilePosition], set[TilePosition]]:
		"""
			This analyses the matrix and returns the sets of mine and safe positions that can be found from the matrix
			
			Inputs:
				- mat: the matrix to be analysed
				- var_list: the list of variables, which links the position in the matrix to an actual tile
			Outputs:
				- mines: the found mines
				- safes: the found safe tiles
		"""
		
		mines: set[TilePosition] = set()  #initialize the sets to keep track of mines and safes
		safes: set[TilePosition] = set()
		
		#for each row in the matrix. Reversed so we go bottom up, which allows us to use previous information to solve subsequent rows
		for row in reversed(mat):
			
			#skip a row if it gives no information
			if all(i == 0 for i in row):
				continue
			
			#split the row into variable coefficients and the result. Ignore the 0 coefficients, as these add no information
			terms: list[tuple[int, float]] = [(key, data) for key, data in enumerate(row[:-1]) if data != 0]
			result: float = row[-1]
			
			#set a lower and upper bound for the mines in this row
			lower_bound: float = 0
			upper_bound: float = 0
			
			#keeps track of which tile contribute to which bounds
			lower_tiles: set[int] = set()
			upper_tiles: set[int] = set()
			
			#for each variable
			for index, coef in terms:
				
				#if the variable is a confirmed mine, it is always included
				#if the variable is in safes, it is never included
				#if the coefficient is positive, it contributes to the upper bound, else it contributes to the lower bound
				if (coef > 0 and var_list[index] not in safes) or var_list[index] in mines:
					upper_bound += coef
					upper_tiles.add(index)
				if (coef < 0 and var_list[index] not in safes) or var_list[index] in mines:
					lower_bound += coef
					lower_tiles.add(index)
			
			#if the result matches the lower bound, add all positives to safes, and negatives to mines
			if result == lower_bound:
				for tile in lower_tiles:
					mines.add(var_list[tile])
				for tile in upper_tiles:
					if var_list[tile] not in mines:
						safes.add(var_list[tile])
			
			#if the result matches the upper bound, add all positives to mines, and negatives to safes
			elif result == upper_bound:
				for tile in upper_tiles:
					mines.add(var_list[tile])
				for tile in lower_tiles:
					if var_list[tile] not in mines:
						safes.add(var_list[tile])
		
		#return results
		return mines, safes
	
	def _find_progress(self, answer_board: Board, new_safe_set: set[TilePosition], old_borders: set[TilePosition]) -> tuple[set[TilePosition], set[TilePosition], set[TilePosition]]:
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
		
		#get the position of all the border tiles
		borders: set[TilePosition] = self.get_border_tiles(answer_board, new_safe_set, old_borders)
		
		#if there aren't any (ie they are all surrounded by flags, the board is unsolvable
		if not borders:
			return set(), set(), set()
		
		#get information for matrix building
		var_dict: dict[TilePosition:list[TilePosition]] = self._build_var_dict(borders, answer_board)
		var_list: list[TilePosition] = self._build_var_list(var_dict)
		
		#build the matrix
		mat: Matrix = self._build_mat(var_dict, var_list, answer_board)
		
		#conduct Gaussian elimination to make the matrix easier to solve
		new_mat: Matrix = self._row_echelon(mat)
		
		#get the positions of all the mine and safe tiles from the matrix
		mines, safes = self._analyse_matrix(new_mat, var_list)
		
		#return results.
		return mines, safes, borders
