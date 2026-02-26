from MainPrograms.BoardGeneratorPrograms.SpaceBoardGenerator import SpaceBoardGenerator
from MainPrograms.BoardGeneratorPrograms.Seed import Seed
from MainPrograms.Solvers.OffsetBoardSolver import OffsetBoardSolver

type Board = list[list[int]]
type TilePosition = tuple[int, int]


class OffsetBoardGenerator(SpaceBoardGenerator):
	def __init__(self, n_cols: int, n_rows: int, start_pos: TilePosition, minecount: int, seed: str, space_count: int, directions: list[TilePosition], process_count: int = 0) -> None:
		"""
			Constructor method for OffsetBoardGenerator class

			Inputs:
				- n_cols: number of columns in the board
				- n_rows: number of rows in the board
				- start_pos: the tile the user clicks to start the game
				- minecount: the number of mines the user has to find
				- seed: the seed used to generate the board. Default is "", which indicates that a random seed should be generated.
				- space_count: the number of empty (space) tiles to be generated
				- directions: the tiles to be treated as adjacent
				- process_count: the number of simultaneous boards generated in parallel
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
				- self._directions: the positions of the "adjacent" tiles
		"""
		
		super().__init__(n_cols, n_rows, start_pos, minecount, seed, space_count, process_count=process_count)
		self._directions: list[TilePosition] = directions
		self._seed_gen: Seed = Seed(n_cols=self._n_cols, n_rows=self._n_rows, minecount=self._minecount, start_pos=self._start_pos, directions=self._directions, seed=self._seed)
		self._solver: OffsetBoardSolver = OffsetBoardSolver(n_cols=self._n_cols, n_rows=self._n_rows, minecount=self._minecount, start_pos=self._start_pos, directions=self._directions)
	
	def _get_adjacent_tiles_reversed(self, pos: TilePosition) -> set[TilePosition]:
		"""
			Gives the positions of the adjacent tiles

			Inputs:
				- pos: the target tile position
			Returns:
				- output_set: the list of adjacent tiles
		"""
		output_set: set[TilePosition] = set()  # initialise output set
		
		#invert the directions
		dirs = [(-row, -col) for row, col in self._directions]
		
		for row, col in dirs:  # for each adjacent tile
			rx, ry = pos[0] + row, pos[1] + col
			if 0 <= pos[0] + row < self._n_rows and 0 <= pos[1] + col < self._n_cols:  # if position within the board
				if self._board[rx][ry] != -3:
					output_set.add((pos[0] + row, pos[1] + col))  # add it to the set
		
		return output_set
	
	def _generate_board_space(self, space_positions: set[TilePosition] = None) -> tuple[Board, set[TilePosition]]:
		"""
			Returns a board based on _mine_pos which is obtained through the seed class

			Inputs:
				- space_positions: the positions of all spaces that need to be carried forwards to the next iteration
			Outputs:
				- target_board: the board generated
				- spaces: the positions of all empty tiles
		"""
		mines: set[TilePosition] = set()  # initialize variables
		target_board: Board = [[0 for _ in range(self._n_cols)] for _ in range(self._n_rows)]
		
		index = 0
		while len(mines) < self._minecount:  # while not all mines placed
			current_mine: TilePosition = self._mine_positions[index]
			if target_board[current_mine[0]][current_mine[1]] != -1:  # if mine not already placed
				mines.add(current_mine)  # place mine
				target_board[current_mine[0]][current_mine[1]] = -1
				
				for row, col in self._get_adjacent_tiles_reversed(current_mine):  # update all numbers
					if target_board[row][col] != -1:  # exclude mines to not overwrite them
						target_board[row][col] += 1
			index += 1  # look at next position
		
		#generate a list of valid mine positions
		space_positions = self._seed_gen.generate_mines_list(includes=space_positions, excludes=mines)
		spaces: set[TilePosition] = set()
		
		while len(spaces) < self._space_count:  # while not all spaces placed
			current_space = space_positions[index]
			if target_board[current_space[0]][current_space[1]] >= 0:  # if space not already placed
				spaces.add(current_space)  # place space
				target_board[current_space[0]][current_space[1]] = -3
			index += 1  # look at next position
		
		return target_board, spaces
