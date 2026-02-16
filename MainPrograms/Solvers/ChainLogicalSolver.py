from MainPrograms.Solvers.LogicalSolver import LogicalSolver
from MainPrograms.Solvers.ChainMatrixSolver import ChainMatrixSolver

type Board = list[list[int]]
type Matrix = list[list[float]]
type TilePosition = tuple[int, int]


class ChainLogicalSolver(LogicalSolver, ChainMatrixSolver):
	def __init__(self, n_cols: int, n_rows: int, start_pos: TilePosition, minecount: int) -> None:
		"""
			Constructor method for ChainLogicalSolver class

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
	
	def _resolve_chain(self, mines: set[TilePosition]) -> tuple[set[TilePosition], set[TilePosition]]:
		"""
			Marks all tiles orthogonally adjacent to a pair of mines as safe
			
			Inputs:
				- mines: the set of previously unpaired mines
			Outputs:
				- safes: the safe tiles it finds from its logical deductions according to this rule
				- new_mines_in_chains: the set of newly paired mines
		"""
		
		#initialize variables
		safes: set[TilePosition] = set()
		new_mines_in_chains: set[TilePosition] = set()
		
		#for each mine
		for mine_row, mine_col in mines:
			
			#store mine for future use
			mine = (mine_row, mine_col)
			
			#get the positions of adjacent tiles
			orthogonal_positions: set[TilePosition] = self.get_orthogonal_adj(mine)
			
			#initialize the variables for this iteration
			pair: bool = False
			new_safes: set[TilePosition] = set()
			target_mine: TilePosition = (-1, -1)  #to avoid IDE complaining that target_mine may be referenced before assignment - it shouldn't be
			
			#for each orthogonally adjacent tile
			for target_row, target_col in orthogonal_positions:
				target_mine: TilePosition = (target_row, target_col)
				
				#if target is a mine, form a mine pair
				if target_mine in mines:
					new_mines_in_chains.update({mine, target_mine})
					pair = True
				
				#else store the safe tile in case it is needed
				else:
					new_safes.add(target_mine)
			
			#if a pair is successfully formed
			if pair:
				#add all the orthogonally adjacent tiles to the set of safe tiles
				safes.update(new_safes)
				for position in self.get_orthogonal_adj(target_mine):
					safes.add(position)
				safes.remove(mine)
		
		return safes, new_mines_in_chains
	
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
		
		# initialize the test board. The start position is always 0
		test_board: list[list[int]] = [[-2 for _ in range(self._n_cols)] for _ in range(self._n_rows)]
		test_board[self._start_pos[0]][self._start_pos[1]] = 0
		
		# resolve first iteration. The tiles around the start position are always safe
		start_adjacency: set[TilePosition] = self._get_adjacent_tiles(self._start_pos)
		start_adjacency.add(self._start_pos)
		for row, col in start_adjacency:
			test_board[row][col] = answer_board[row][col]
		
		# initialize these variables
		old_borders: set[TilePosition] = set().union({self._start_pos})
		new_safes: set[TilePosition] = set(start_adjacency)
		mines: set[TilePosition] = set()
		free_mines: set[TilePosition] = set()
		chain_mines: set[TilePosition] = set()
		
		# while there is still a tile that is covered
		while self._check_for_covered_tile(test_board):
			
			# run logical solver
			new_mines, new_safes, old_borders = self._find_logical_progress(test_board, new_safes, old_borders)
			chain_safes, new_chain_mines = self._resolve_chain(free_mines)
			new_safes.update(chain_safes)
			chain_mines.update(new_chain_mines)
			
			# if nothing found, run the matrix solver
			if not (new_mines or new_safes):
				new_mines, new_safes, old_borders = self._find_progress_chain(test_board, new_safes, old_borders, free_mines)
				
				# if nothing found, the board is unsolvable
				if not (new_mines or new_safes):
					return mines, False
			
			# update the safe tiles
			for row, col in new_safes:
				test_board[row][col] = answer_board[row][col]
			
			# update the mines
			for row, col in new_mines:
				test_board[row][col] = -1
				mines.add((row, col))
			
			#update free mines set
			free_mines = mines - chain_mines
		
		# return results
		return set(), True