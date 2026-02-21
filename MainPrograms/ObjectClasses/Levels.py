import sqlite3
import os
import sys

type TilePosition = tuple[int, int]
type Board = list[list[int]]


def database_path(relative_path):
	"""
		Converts a relative path to a database into an absolute path
		Additionally creates a new directory to store the database

		Inputs:
			- relative_path: the relative path from the root directory of the target database
		Outputs:
			- full_path: the absolute path to the target database
	"""
	
	# if running as a bundled process (ie as an exe)
	if getattr(sys, "frozen", False):
		base_path = os.path.dirname(sys.executable)
	
	# if running as a normal .py file
	else:
		base_path = os.path.abspath(".")
	
	# create the full path
	full_path = os.path.join(base_path, relative_path)
	
	# create the directory for the database
	os.makedirs(os.path.dirname(full_path), exist_ok=True)
	
	# return the path
	return full_path

# noinspection PyProtectedMember
def resource_path(relative_path):
	if hasattr(sys, "_MEIPASS"):
		return os.path.join(sys._MEIPASS, relative_path)
	return os.path.join(os.path.abspath("."), relative_path)

class LevelManager:
	def __init__(self) -> None:
		"""
			Constructor method for the LevelManager class

			Inputs:
				- None
		"""
		
		self.connection = sqlite3.connect(database_path("MainPrograms/ObjectClasses/level.db"))
		self.cursor = self.connection.cursor()
		#self.cursor.execute("DROP TABLE level;")
		#self.cursor.execute("DROP TABLE tutorial;")
		self.cursor.execute("""
			CREATE TABLE IF NOT EXISTS level (
			level_id INTEGER PRIMARY KEY AUTOINCREMENT,
			level_board TEXT NOT NULL,
			revealed_tiles TEXT NOT NULL
			);
			""")
		self.cursor.execute("""
			CREATE TABLE IF NOT EXISTS tutorial (
			id INT PRIMARY KEY,
			private_board TEXT NOT NULL,
			public_board TEXT NOT NULL,
			description TEXT NOT NULL
			);
			""")
	
	def check_table_exists(self):
		self.cursor.execute("SELECT COUNT(*) FROM level")
		return self.cursor.fetchall()[0][0] >= 2
	
	@staticmethod
	def board_to_str(board: Board) -> str:
		"""
			Converts a board into a single string
			
			Inputs:
				- board: the board to be converted
			Output:
				- board_str: the converted board
		"""
		
		#initialize the board string
		board_str: str = "["
		
		#for every row in the board
		for row in range(len(board)):
			
			#start with a new open bracket
			board_str += "["
			
			#for every item in the row
			for col in range(len(board[0])):
				
				#add it to the string
				board_str += f"{board[row][col]}"
				
				#if not the final item in the row, add a comma
				if col != len(board[0]) - 1:
					board_str += ","
			
			#end with a close bracket
			board_str += "]"
			
			#if not the final row in the board, add a comma
			if row != len(board) - 1:
				board_str += ","
		
		#end with a close bracket
		board_str += "]"
		return board_str
	
	def init_database_level(self) -> None:
		#for each level
		for level_id in range(1, 7):
			
			#initialize the board and revealed tiles=
			board: Board = []
			revealed_tile: TilePosition = (0, 0)
			
			#get the board and revealed tile for the given level
			match level_id:
				
				# level 1
				case 1:
					revealed_tile = (0, 0)
					board = [
						[0, 0, 1, -1, 1],
						[1, 1, 1, 1, 1],
						[-1, 1, 0, 0, 0],
						[1, 1, 1, 1, 1],
						[0, 0, 1, -1, 1]
					]
				
				# level 2
				case 2:
					revealed_tile = (1, 2)
					board = [
						[-1, 2, 0, 1, 2, 2],
						[-1, 2, 0, 1, -1, -1],
						[1, 2, 1, 2, 2, 2],
						[0, 1, -1, 2, 1, 1],
						[1, 2, 1, 2, -1, 1],
						[-1, 1, 0, 1, 1, 1]
					]
				
				# level 3
				case 3:
					revealed_tile = (4, 4)
					board = [
						[-1, 2, -1, 3, -1, 3, 1],
						[2, 3, 1, 3, -1, -1, 3],
						[-1, 1, 0, 1, 3, -1, -1],
						[3, 3, 1, 0, 1, 3, 3],
						[-1, -1, 3, 1, 0, 1, -1],
						[3, -1, -1, 3, 1, 3, 2],
						[1, 3, -1, 3, -1, 2, -1]
					]
				
				# level 4
				case 4:
					revealed_tile = (1, 1)
					board = [
						[0, 0, 1, -1, 3, -1, -1, -1],
						[0, 0, 2, 3, -1, 3, -1, -1],
						[1, 2, 2, -1, 3, 3, 2, 2],
						[-1, 2, -1, 4, -1, 2, 2, 1],
						[1, 2, 3, -1, 4, -1, 2, -1],
						[0, 1, 4, -1, 4, 1, 2, 1],
						[0, 1, -1, -1, 2, 1, 1, 1],
						[1, 1, 2, 2, 1, 1, -1, 1]
					]
				
				# level 5
				case 5:
					revealed_tile = (0, 1)
					board = [
						[0, 0, 1, 1, -1, 2, 2, -1, -1],
						[1, 2, 1, 2, 1, 2, -1, 4, -1],
						[-1, 2, -1, 1, 1, 2, 2, 3, 2],
						[1, 2, 1, 1, 1, -1, 1, 2, -1],
						[1, 2, 2, 1, 2, 2, 3, 3, -1],
						[1, -1, -1, 1, 1, -1, 2, -1, 2],
						[1, 2, 3, 2, 3, 3, 5, 3, 2],
						[0, 0, 1, -1, 2, -1, -1, -1, 1],
						[0, 0, 1, 1, 2, 3, -1, 3, 1]
					]
				
				# final boss
				case 6:
					revealed_tile = (6, 7)
					board = [
						[1, -1, -1, -1, -1, -1, 1, 0, 0, 0],
						[1, 3, 5, -1, 4, 2, 1, 1, 2, 2],
						[0, 1, -1, 2, 1, 0, 1, 3, -1, -1],
						[0, 2, 2, 3, 2, 3, 4, -1, -1, -1],
						[1, 2, -1, 2, -1, -1, -1, -1, 6, -1],
						[-1, 5, 3, 3, 3, -1, 4, 2, 4, -1],
						[-1, -1, -1, 1, 2, 2, 2, 0, 2, -1],
						[3, 5, 3, 3, 2, -1, 1, 1, 2, 2],
						[-1, 2, -1, 3, -1, 5, 4, 4, -1, 3],
						[1, 2, 1, 3, -1, -1, -1, -1, -1, -1]
					]
			
			#convert them into a string
			board_str: str = self.board_to_str(board)
			revealed_tiles_str: str = f"({revealed_tile[0]},{revealed_tile[1]})"
			
			#add it to the database
			self.cursor.execute("""
			INSERT INTO level
			(level_board, revealed_tiles)
			VALUES (?, ?);
			""", (board_str, revealed_tiles_str))
	
	def init_database_tutorial(self) -> None:
		#store the number of sublevels in each level
		sublevel_count_list: list[int] = [3, 2, 1, 1, 2, 3, 1, 1, 1, 1]
		
		#initialize a list contain all the private boards for each level and sublevel
		private_board_list: list[list[Board]] = [
			#level 1
			[
				#sublevel 1
				[
					[1, 1, 1],
					[1, -1, 1],
					[1, 1, 1]
				],
				
				#sublevel 2
				[
					[1, 2, 2, 1],
					[1, -1, -1, 1],
					[1, 2, 2, 1]
				],
				
				#sublevel 3
				[
					[-2, -2, -2, -2, -2],
					[-2, -1, -1, -1, -2],
					[-3, -3, 3, -3, -3]
				]
			],
			
			#level 2
			[
				#sublevel 1
				[
					[1, -5, -2],
					[1, -1, -5],
					[1, 1, 1]
				],
				
				#sublevel 2
				[
					[-3, -5, -2, -2],
					[-3, -1, -1, -5],
					[-3, 2, 2, -3]
				]
			],
			
			#level 3
			[
				#sublevel 1
				[
					[-3, -2, -2, -5],
					[-3, 1, 1, -3]
				]
			],
			
			#level 4
			[
				#sublevel 1
				[
					[-5, -5, -5],
					[-2, 1, -2],
					[1, 1, 1]
				]
			
			],
			
			#level 5
			[
				#sublevel 1
				[
					[-1, -2, -2],
					[-2, 3, 1],
					[-2, 1, -3]
				],
				
				#sublevel 2
				[
					[-5, -2, -2, -3],
					[-2, 2, 1, -3],
					[-2, 1, -3, -3],
					[-3, -3, -3, -3]
				]
			],
			
			#level 6
			[
				#sublevel 1
				[
					[-5, -2, -2, -1],
					[-5, 1, 2, -3],
					[-5, -2, -2, -3]
				],
				
				#sublevel 2
				[
					[-5, -2, -2, -3],
					[-5, 1, 2, -3],
					[-5, -2, -2, -1]
				],
				
				#sublevel 3
				[
					[-5, -2, -2, -1],
					[-3, 1, 2, -3]
				]
			],
			
			#level 7
			[
				#sublevel 1
				[
					[-1, -5, -1],
					[1, 2, 1]
				]
			],
			
			#level 8
			[
				#sublevel 1
				[
					[-5, -5, -1, -1, -5, -5],
					[-3, 1, 2, 2, 1, -3]
				]
			],
			
			#level 9
			[
				#sublevel 1
				[
					[-3, -5, -1, -5, -3],
					[-3, 1, 1, 1, -3]
				]
			],
			
			#final boss
			[
				[
					[0, 1, -1, 2, -1, 1, 1, 1, 1, 0],
					[1, 2, 1, 2, 1, 1, 1, -1, 1, 0],
					[-1, 1, 0, 0, 0, 0, 1, 1, 2, 1],
					[1, 1, 1, 2, 2, 1, 1, 1, 2, -1],
					[0, 1, 2, -1, -1, 1, 1, -1, 2, 1],
					[1, 1, -1, 3, 2, 1, 1, 1, 1, 0],
					[1, 1, 1, 1, 0, 0, 0, 0, 0, 0],
					[1, 1, 1, 1, 2, 2, 2, 2, 1, 1],
					[-1, 2, 1, -1, 2, -1, -1, 2, -1, 1],
					[-1, 2, 1, 1, 2, 2, 2, 2, 1, 1]
				]
			]
		]
		
		#initialize a list contain all the public boards for each level and sublevel
		public_board_list: list[list[Board]] = [
			# level 1
			[
				# sublevel 1
				[
					[1, 1, 1],
					[1, -2, 1],
					[1, 1, 1]
				],
				
				# sublevel 2
				[
					[1, 2, 2, 1],
					[1, -2, -2, 1],
					[1, 2, 2, 1]
				],
				
				# sublevel 3
				[
					[-2, -2, -2, -2, -2],
					[-2, -2, -2, -2, -2],
					[-3, -3, 3, -3, -3]
				]
			],
			
			# level 2
			[
				# sublevel 1
				[
					[1, -2, -2],
					[1, -2, -2],
					[1, 1, 1]
				],
				
				# sublevel 2
				[
					[-3, -2, -2, -2],
					[-3, -2, -2, -2],
					[-3, 2, 2, -3]
				]
			],
			
			# level 3
			[
				# sublevel 1
				[
					[-3, -2, -2, -2],
					[-3, 1, 1, -3]
				]
			],
			
			# level 4
			[
				# sublevel 1
				[
					[-2, -2, -2],
					[-2, 1, -2],
					[1, 1, 1]
				]
			
			],
			
			# level 5
			[
				# sublevel 1
				[
					[-2, -2, -2],
					[-2, 3, 1],
					[-2, 1, -3]
				],
				
				# sublevel 2
				[
					[-2, -2, -2, -3],
					[-2, 2, 1, -3],
					[-2, 1, -3, -3],
					[-3, -3, -3, -3]
				]
			],
			
			# level 6
			[
				# sublevel 1
				[
					[-2, -2, -2, -2],
					[-2, 1, 2, -3],
					[-2, -2, -2, -3]
				],
				
				# sublevel 2
				[
					[-2, -2, -2, -3],
					[-2, 1, 2, -3],
					[-2, -2, -2, -2]
				],
				
				# sublevel 3
				[
					[-2, -2, -2, -2],
					[-3, 1, 2, -3]
				]
			],
			
			# level 7
			[
				# sublevel 1
				[
					[-2, -2, -2],
					[1, 2, 1]
				]
			],
			
			# level 8
			[
				# sublevel 1
				[
					[-2, -2, -2, -2, -2, -2],
					[-3, 1, 2, 2, 1, -3]
				]
			],
			
			# level 9
			[
				# sublevel 1
				[
					[-3, -2, -2, -2, -3],
					[-3, 1, 1, 1, -3]
				]
			],
			
			# final boss
			[
				[
					[0, -2, -2, -2, -2, -2, -2, -2, -2, -2],
					[-2, -2, -2, -2, -2, -2, -2, -2, -2, -2],
					[-2, -2, -2, -2, -2, -2, -2, -2, -2, -2],
					[-2, -2, -2, -2, -2, -2, -2, -2, -2, -2],
					[-2, -2, -2, -2, -2, -2, -2, -2, -2, -2],
					[-2, -2, -2, -2, -2, -2, -2, -2, -2, -2],
					[-2, -2, -2, -2, -2, -2, -2, -2, -2, -2],
					[-2, -2, -2, -2, -2, -2, -2, -2, -2, -2],
					[-2, -2, -2, -2, -2, -2, -2, -2, -2, -2],
					[-2, -2, -2, -2, -2, -2, -2, -2, -2, -2]
				]
			]
		]
		
		#initialze a variable that contains the path to the TutorialDescriptions folder
		common_path: str = "MainPrograms/ObjectClasses/TutorialDescriptions/"
		
		#for each level
		for i in range(1, len(sublevel_count_list) + 1):
			
			#get the number of sublevels in that level
			sublevel_count = sublevel_count_list[i - 1]
			
			#for each sublevel
			for sublevel in range(1, sublevel_count + 1):
				#get the private board from the list and convert it into a string
				private_board: Board = private_board_list[i - 1][sublevel - 1]
				private_board_str: str = self.board_to_str(private_board)
				
				# get the public board from the list and convert it into a string
				public_board: Board = public_board_list[i - 1][sublevel - 1]
				public_board_str: str = self.board_to_str(public_board)
				
				#add it into the database, alongside the path to the photo containing the description for the sublevel
				self.cursor.execute("""
							INSERT INTO tutorial
							(id, private_board, public_board, description)
							VALUES (?, ?, ?, ?);
							""",
									(int(str(i) + str(sublevel)),
									 private_board_str,
									 public_board_str,
									 common_path + str(i) + str(sublevel) + ".png"))
	
	def get_level(self, level: int) -> tuple[Board, set[TilePosition]]:
		"""
			Gets the level from the database
			
			Inputs:
				- level: the id of the level you want to get
			Outputs:
				- level_board: the level's board
				- revealed_tiles: the starting point for the tile
		"""
		#get the level board from the database. Remove the first and last pair of square brackets
		self.cursor.execute(f"SELECT level_board FROM level WHERE level_id = {level}")
		level_board_str: str = self.cursor.fetchall()[0][0][2:-2]
		
		#get the individual rows
		level_board_items: list[str] = [level_board_item for level_board_item in level_board_str.split("],[")]
		
		#convert the rows into the final board
		level_board: Board = [[int(value) for value in level_board_item.split(",")] for level_board_item in level_board_items]
		
		#get the revealed tiles from the database and remove the brackets
		self.cursor.execute(f"SELECT revealed_tiles FROM level WHERE level_id = {level}")
		revealed_tile_str: str = self.cursor.fetchall()[0][0][1:-1]
		
		#initialize a set
		revealed_tiles: set[TilePosition] = set()
		
		#convert the string into a tuple of ints
		revealed_tile: TilePosition = int(revealed_tile_str.split(",")[0]), int(revealed_tile_str.split(",")[1])
		
		#add it to the set
		revealed_tiles.add(revealed_tile)
		
		return level_board, revealed_tiles
	
	def get_tutorial(self, level: int, sublevel: int = 1) -> tuple[Board, Board, str] | tuple[Board, set[TilePosition]]:
		"""
			Gets the tutorial level from the database

			Inputs:
				- level: the level you want to get
				- sublevel: teh sublevel from the that tutorial
			Outputs:
				- level_board: the level's board
				- revealed_tiles: the starting point for the tile
		"""
		#initialize the tutorial id
		tutorial_id = int(str(level) + str(sublevel))
		
		#get the private board from the database
		self.cursor.execute(f"SELECT private_board FROM tutorial WHERE id={tutorial_id};")
		private_board_str = self.cursor.fetchone()[0][2:-2]
		
		# get the public board from the database
		self.cursor.execute(f"SELECT public_board FROM tutorial WHERE id={tutorial_id};")
		public_board_str = self.cursor.fetchone()[0][2:-2]
		
		# get the individual rows
		private_board_items: list[str] = [level_board_item for level_board_item in private_board_str.split("],[")]
		
		#convert the rows into the final board
		private_board: Board = [[int(value) for value in level_board_item.split(",")] for level_board_item in private_board_items]
		
		# get the individual rows
		public_board_items: list[str] = [level_board_item for level_board_item in public_board_str.split("],[")]
		
		# convert the rows into the final board
		public_board: Board = [[int(value) for value in level_board_item.split(",")] for level_board_item in public_board_items]
		
		if level == 10:
			revealed_tiles = set()
			revealed_tiles.add((0, 0))
			
			return private_board, revealed_tiles
		
		#get the description path from the database
		self.cursor.execute(f"SELECT description FROM tutorial WHERE id={tutorial_id};")
		description_path: str = self.cursor.fetchall()[0][0]
		
		return private_board, public_board, description_path
	
	def close_connection(self) -> None:
		self.connection.commit()
		self.connection.close()


if __name__ == "__main__":
	temp = LevelManager()
	temp.init_database_level()
	temp.init_database_tutorial()
	temp.close_connection()