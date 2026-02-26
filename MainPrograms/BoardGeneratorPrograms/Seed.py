import string  #this is not strictly needed, but it effectively replaces ["a", "b", ..., "z"] etc
import random
import multiprocessing as mp

type TilePosition = tuple[int, int]


class Seed:
	def __init__(self, n_cols, n_rows, minecount, start_pos, directions, seed: str = "") -> None:
		"""
			Constructor method for Board class

			Inputs:
				- seed: The seed to be used for random generation
			Initializes:
				- self._seed: The seed to be used for random generation
				- self._n_cols: number of columns in the board
				- self._n_cols: number of rows in the board
				- self._start_pos: the tile the user clicks to start the game
				- self._minecount: the number of mines the user has to find
		"""
		#validation
		if seed == "":  #if seed is empty or not given
			seed = self._gen_seed()
		elif len(seed) > 10 or any(char not in string.digits + string.ascii_letters + " " for char in seed):  #if seed is invalid
			raise ValueError(f"Invalid seed: {seed}")
		
		self._n_cols: int = n_cols  #initialize all variables
		self._n_rows: int = n_rows
		self._minecount: int = minecount
		self._start_pos: TilePosition = start_pos
		self._seed: str = seed
		self._directions: list[TilePosition] = directions
		
		#include itself
		self._directions.append((0, 0))
		
		random.seed(self._seed)  #initialize the internal seed
	
	@staticmethod
	def _gen_seed() -> str:
		"""
			Create a random 10 character string of alphanumeric characters
			
			Inputs
				- None
			Returns
				- seed: the seed generated
		"""
		# choices produces a list, not a string, so .join is used to convert to a string
		return "".join(random.choices(population=string.digits + string.ascii_letters, k=10))
	
	def get_seed(self) -> str:
		"""
			Getter for seed attribute

			Inputs
				- None
			Returns
				- self._seed: the seed attribute
		"""
		return self._seed
	
	def give_random_tile(self, *, select_from: set[TilePosition] = None, excludes: set[TilePosition] = None) -> TilePosition:
		"""
			Returns a random valid tile

			Inputs
				- select_from: the list of tiles to select a position from
				- excludes: the list of tiles to not select from
			Returns
				- tile: the tile selected
		"""
		#if select_from is defined, return a value from it
		if select_from not in [None, set()]:
			return random.choice(list(select_from))
		
		#if the select from options is empty, return null tile
		if select_from == set():
			return -1, -1
		
		#generate a random tile position
		tile = (random.randrange(self._n_rows), random.randrange(self._n_cols))
		
		#avoids type error
		if excludes is None:
			return tile
		
		#repeat until a valid tile is chosen
		while tile in excludes:
			tile = (random.randrange(self._n_rows), random.randrange(self._n_cols))
		
		#return results
		return tile
	
	def generate_mines_list(self, *, includes: set[TilePosition] = None, excludes: set[TilePosition] = None, process_count: int = 0, iteration: int = 0) -> list[TilePosition]:
		"""
			Generator for the mines list. It generates a list of all positions on the board in a random order, excluding
			the start position, the 8 adjacent tiles and any safe tiles given as an argument

			Inputs
				- includes: any tiles that must be included at the start of the list
				- excludes: any tiles that must not be included in the list
			Returns
				- positions: the list of positions generated
		"""
		if excludes is None:
			excludes = set()
		if includes is None:
			includes = set()
		
		#Make sure that the first tile is a 0 by making sure that the tile surround it cannot be mines
		excludes.update(set((row + self._start_pos[0], col + self._start_pos[1]) for row, col in self._directions))
		positions: list[TilePosition] = list(includes.copy())
		extra_positions: list[TilePosition] = ([  #list of all valid positions
			(row, col) for row in range(self._n_rows) for col in range(self._n_cols) if (row, col) not in excludes and (row, col) not in includes
		])
		
		# randomize the order
		if iteration == 0:
			for i in range(process_count):
				random.shuffle(extra_positions)
		for i in range(mp.cpu_count()):
			random.shuffle(extra_positions)
		
		#return the positions
		positions.extend(extra_positions)
		return positions