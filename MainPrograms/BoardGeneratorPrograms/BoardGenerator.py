from MainPrograms.BoardGeneratorPrograms.Seed import Seed
from MainPrograms.Solvers.LogicalSolver import LogicalSolver
import cProfile
import io
import pstats
from multiprocessing import Event

type Board = list[list[int]]
type TilePosition = tuple[int, int]


class BoardGenerator:
	def __init__(self, n_cols: int, n_rows: int, start_pos: TilePosition, minecount: int, seed: str = "", process_count: int = 0) -> None:
		"""
			Constructor method for BoardGenerator class

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
		self._n_cols: int = n_cols  #initialize variables from parameters
		self._n_rows: int = n_rows
		self._start_pos: TilePosition = start_pos
		self._minecount: int = minecount
		self._seed: str = seed
		
		self._board: Board = [[-2 for _ in range(self._n_cols)] for _ in range(self._n_rows)]  #initialize other variables and objects
		self._directions: list[TilePosition] = [(x, y) for x in [-1, 0, 1] for y in [-1, 0, 1]]
		self._solver: LogicalSolver = LogicalSolver(n_cols=self._n_cols, n_rows=self._n_rows, minecount=self._minecount, start_pos=self._start_pos)
		self._seed_gen: Seed = Seed(n_cols=self._n_cols, n_rows=self._n_rows, minecount=self._minecount, start_pos=self._start_pos, directions=self._directions, seed=self._seed)
		self._mine_positions: list[TilePosition] = self._seed_gen.generate_mines_list(process_count=process_count)
		
		self._directions.remove((0, 0))  #does not include itself
	
	def get_board(self) -> Board:
		"""
			Getter for self.board attribute
			
			Inputs
				- None
			Returns
				- self.board: the board attribute
		"""
		return self._board
	
	def _get_adjacent_tiles(self, pos: TilePosition) -> set[TilePosition]:
		"""
			Gives the positions of the adjacent tiles

			Inputs:
				- pos: the target tile position
			Returns:
				- output_set: the list of adjacent tiles
		"""
		output_set: set[TilePosition] = set()  #initialise output set
		
		for row, col in self._directions:  #for each adjacent tile
			if 0 <= pos[0] + row < self._n_rows and 0 <= pos[1] + col < self._n_cols:  #if position within the board
				output_set.add((pos[0] + row, pos[1] + col))  #add it to the set
		
		return output_set
	
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
		
		index: int = 0
		while len(mines) < self._minecount:  #while not all mines placed
			current_mine: TilePosition = self._mine_positions[index]
			if target_board[current_mine[0]][current_mine[1]] != -1:  #if mine not already placed
				mines.add(current_mine)  #place mine
				target_board[current_mine[0]][current_mine[1]] = -1
				
				for row, col in self._get_adjacent_tiles(current_mine):  #update all numbers
					if target_board[row][col] != -1:  #exclude mines to not overwrite them
						target_board[row][col] += 1
			index += 1  #look at next position
		
		return target_board
	
	def _reset_board(self, old_mines: set[TilePosition]) -> None:
		"""
			Resets the board so that a new one can be trialled

			Inputs:
				- None
			Modifies:
				- self.board: the board to be generated
				- self._mine_positions: the mines used to generate the board
		"""
		
		self._board: Board = [[-2 for _ in range(self._n_cols)] for _ in range(self._n_rows)]
		self._mine_positions: list[TilePosition] = self._seed_gen.generate_mines_list(includes=old_mines)
	
	def generate_no_guess_board(self) -> None:
		"""
			Modifies self.board to generate a board.

			Inputs:
				- None
			Modifies:
				- self.board: the board generated
		"""
		
		# initialize variables
		solvable: bool = False
		mines: set[TilePosition] = set()
		count: int = 0
		
		#loop until a solvable board is found
		while not solvable:
			
			#if stuck, do a full reset
			if count == 3:
				self._reset_board(set())
				count = 0
			#if not stuck, only reset unsolved mines
			else:
				self._reset_board(mines)
				count += 1
			
			#generate a board to test
			self._board = self._generate_board()
			
			#solve the board, and keep track of solved mines
			mines, solvable = self._solver.solve(self._board)
	
	def generate_no_guess_board_parallel(self, start_event: Event) -> None:
		"""
			Modifies self.board to generate a board.

			Inputs:
				- None
			Modifies:
				- self.board: the board generated
		"""
		
		# initialize variables
		mines: set[TilePosition] = set()
		count: int = 0
		
		# loop until a solvable board is found
		while not start_event.is_set():
			
			# if stuck, do a full reset
			if count == 3:
				self._reset_board(set())
				count = 0
			# if not stuck, only reset unsolved mines
			else:
				self._reset_board(mines)
				count += 1
			
			# generate a board to test
			self._board = self._generate_board()
			
			# solve the board, and keep track of solved mines
			mines, solvable = self._solver.solve(self._board)
			
			# terminate the process early if another process finds a board first
			if start_event.is_set():
				break
			
			#if the board is solvable
			if solvable:
				
				#if no other board has been solved
				if not start_event.is_set():
					start_event.set()
				break
