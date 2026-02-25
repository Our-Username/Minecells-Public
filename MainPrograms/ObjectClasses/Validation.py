import sqlite3
import os
import sys

from MainPrograms.ObjectClasses.ObjectControl import ObjectControl
from MainPrograms.Queue import Queue

type TilePosition = tuple[int, int]
type Board = list[list[int]]


def database_path(relative_path):
	if getattr(sys, "frozen", False):
		base_path = os.path.dirname(sys.executable)
	else:
		base_path = os.path.abspath(".")
	
	full_path = os.path.join(base_path, relative_path)
	os.makedirs(os.path.dirname(full_path), exist_ok=True)
	return full_path


# noinspection PyProtectedMember
def resource_path(relative_path):
	if hasattr(sys, "_MEIPASS"):
		return os.path.join(sys._MEIPASS, relative_path)
	return os.path.join(os.path.abspath("."), relative_path)


class Validation:
	def __init__(self, object_controller: ObjectControl) -> None:
		"""
			Constructor method for the Validation class
			
			Inputs:
				- object_controller: the object controller object
			Initializes:
				- self._object_controller: the object controller object
				- self._error_lines: the notifications displayed to the user
		"""
		
		self._object_controller: ObjectControl = object_controller
		self._error_lines: set[str] = set()
		
		self.connection = sqlite3.connect(database_path("MainPrograms/user.db"))
		self.cursor = self.connection.cursor()
		#self.cursor.execute("DROP TABLE user;")
		self.cursor.execute("""
			CREATE TABLE IF NOT EXISTS user (
			user_id INTEGER PRIMARY KEY AUTOINCREMENT,
			username TEXT NOT NULL,
			password TEXT NOT NULL,
			logged_in BOOL,
			custom_score INTEGER,
			levels_score TEXT CHECK (json_valid(levels_score)),
			keybinds TEXT CHECK (json_valid(keybinds)),
			options TEXT CHECK (json_valid(options))
			);
			""")
		#self.cursor.execute("INSERT INTO user (username, password, logged_in, custom_score, levels_score, keybinds, options) VALUES (?, ?, ?, ?, ?, ?, ?)", ("Alice", "password", True, 0, '{"Level 1":-1,"Level 2":-1,"Level 3":-1,"Level 4":-1,"Level 5":-1,"Level 6":-1}', '{"dig":-1,"flag":-2}', '{"chording":"true","theme":"Standard","music":0.8,"sfx":0.5}'))
		self.cursor.execute(f"SELECT user_id FROM user WHERE logged_in={True}")
		user_id_list = self.cursor.fetchall()
		if len(user_id_list) >= 1:
			self.user_id: int | None = user_id_list[0][0]
		else:
			self.user_id: int | None = None
		
		self._error_count: int = 0
	
	# validation for the generator select
	def minecount(self, minecount: int, rows: int, cols: int, old_area: int, spaces: int = 0, generator: str = "Standard") -> bool:
		"""
			Verifies that the minecount is within the valid bounds.
			From testing in iteration 1, I found that the maximum mine density is 20%,
			or if there are spaces, the total mine and space density is at most 19%
		
			Inputs:
				- minecount: the minecount the user input
				- rows: the number of rows the user input
				- cols: the number of columns the user input
				- spaces: the number of spaces the user input (default 0)
				- generator: the current generator selected (default "Standard")
			Output:
				- bool: whether the restrictions placed on the minecount and space count are fulfilled
		"""
		
		#If the minecount is 0, notify the user and return false
		if minecount == 0:
			if not "Must have at least 1 mine" in self._error_lines:
				self._error_lines.add("Must have at least 1 mine")
				self._error_count += 1
				self._object_controller.update_error_box(self._error_lines)
			return False
		else:
			#remove the text telling the user to enter a value as it is no longer true
			if "Must have at least 1 mine" in self._error_lines:
				self._error_lines.remove("Must have at least 1 mine")
				self._error_count -= 1
				self._object_controller.update_error_box(self._error_lines)
		#if there are no rows, return false (the user in informed later)
		if rows == 0 or cols == 0:
			return False
		
		#make some calculations here for readability
		area: int = rows * cols
		mine_density: float = minecount / area
		space_density: float = spaces / area
		
		#if there are no spaces, or of the generator does not take spaces
		if space_density == 0 or generator == "Standard":
			
			#cap mine density at 20%
			if not mine_density <= 0.2:
				
				#notify the user
				if f"Must have at most {int(0.2 * area)} mines" not in self._error_lines:
					self._error_count += 1
					self._error_lines.add(f"Must have at most {int(0.2 * area)} mines")
					self._object_controller.update_error_box(self._error_lines)
			else:
				
				#remove the old notification
				if f"Must have at most {int(0.2 * old_area)} mines" in self._error_lines:
					self._error_lines.remove(f"Must have at most {int(0.2 * old_area)} mines")
					self._error_count -= 1
					self._object_controller.update_error_box(self._error_lines)
			return mine_density <= 0.2
		
		#if the generator takes spaces
		elif generator != "Standard":
			
			#cap space and mine density at 19%
			if not (mine_density + space_density) <= 0.19:
				
				#notify the user
				if f"Must have at most {int(0.19 * area)} spaces and mines in total" not in self._error_lines:
					self._error_count += 1
					self._error_lines.add(f"Must have at most {int(0.19 * area)} spaces and mines in total")
				self._object_controller.update_error_box(self._error_lines)
			else:
				
				#remove the old notification
				if f"Must have at most {int(0.19 * area)} spaces and mines in total" in self._error_lines:
					self._error_lines.remove(f"Must have at most {int(0.19 * area)} spaces and mines in total")
					self._error_count -= 1
					self._object_controller.update_error_box(self._error_lines)
			return (mine_density + space_density) <= 0.19
		return True
	
	def rows(self, rows: int, cols: int) -> bool:
		"""
			Verifies that the amount of rows is within the valid bounds.
			From testing in iteration 1, I found that the reasonable range is 5 - 99

			Inputs:
				- rows: the number of rows the user input
			Output:
				- bool: whether the restriction placed on the rows are fulfilled
		"""
		
		if rows * cols >= 2500:
			self._error_lines.add("Large boards may cause instability")
			self._object_controller.update_error_box(self._error_lines)
		elif "Large boards may cause instability" in self._error_lines:
			self._error_lines.remove("Large boards may cause instability")
			self._object_controller.update_error_box(self._error_lines)
		
		#if row count is invalid
		if not 5 <= rows <= 99:
			
			#notify the user
			if "Must have between 5 and 99 rows" not in self._error_lines:
				self._error_count += 1
				self._error_lines.add("Must have between 5 and 99 rows")
			self._object_controller.update_error_box(self._error_lines)
		else:
			
			#remove old notification
			if "Must have between 5 and 99 rows" in self._error_lines:
				self._error_lines.remove("Must have between 5 and 99 rows")
				self._error_count -= 1
				self._object_controller.update_error_box(self._error_lines)
		return 5 <= rows <= 99
	
	def cols(self, rows: int, cols: int) -> bool:
		"""
			Verifies that the amount of cols is within the valid bounds.
			From testing in iteration 1, I found that the reasonable range is 5 - 99

			Inputs:
				- cols: the number of columns the user input
			Output:
				- bool: whether the restriction placed on the columns are fulfilled
		"""
		
		if rows * cols >= 2500:
			self._error_lines.add("Large boards may cause instability")
			self._object_controller.update_error_box(self._error_lines)
		elif "Large boards may cause instability" in self._error_lines:
			self._error_lines.remove("Large boards may cause instability")
			self._object_controller.update_error_box(self._error_lines)
		
		#if column count is invalid
		if not 5 <= cols <= 99:
			
			#notify the user
			if "Must have between 5 and 99 columns" not in self._error_lines:
				self._error_count += 1
				self._error_lines.add("Must have between 5 and 99 columns")
			self._object_controller.update_error_box(self._error_lines)
		else:
			
			#remove old notification
			if "Must have between 5 and 99 columns" in self._error_lines:
				self._error_lines.remove("Must have between 5 and 99 columns")
				self._error_count -= 1
				self._object_controller.update_error_box(self._error_lines)
		return 5 <= cols <= 99
	
	def difficulty(self, difficulty: int) -> bool:
		"""
			Verifies that the difficulty is within the valid bounds.
			From testing in iteration 1, I found that the reasonable range is 1 - 5

			Inputs:
				- difficulty: the difficulty the user input
			Output:
				- bool: whether the restriction placed on the difficulty are fulfilled
		"""
		
		#if difficulty is invalid
		if not 1 <= difficulty <= 5:
			
			#notify the user
			if "Difficulty must be between 1 and 5" not in self._error_lines:
				self._error_count += 1
				self._error_lines.add("Difficulty must be between 1 and 5")
			self._object_controller.update_error_box(self._error_lines)
		else:
			
			#remove old notification
			if "Difficulty must be between 1 and 5" in self._error_lines:
				self._error_lines.remove("Difficulty must be between 1 and 5")
				self._error_count -= 1
				self._object_controller.update_error_box(self._error_lines)
		return 1 <= difficulty <= 5
	
	@staticmethod
	def _get_adjacent_tiles(pos: TilePosition, directions: list[TilePosition]) -> set[TilePosition]:
		"""
			Gives the positions of the adjacent tiles

			Inputs:
				- pos: the target tile position
			Returns:
				- output_set: the list of adjacent tiles
		"""
		output_set: set[TilePosition] = set()  # initialise output set
		
		for row, col in directions:  # for each adjacent tile
			rx, ry = pos[0] + row, pos[1] + col
			if 0 <= rx < 10 and 0 <= ry < 10:  # if position within the board
				output_set.add((rx, ry))  # add it to the set
		
		return output_set
	
	def offset(self, directions: list[TilePosition]) -> bool:
		"""
			Verify that the new set of directions can provide a complete board.
			To do this, it uses a flood fill algorithm to make sure that the set of
			directions can eventually see every tile in a 10x10 board.
			
			Inputs:
				- directions: the new set of directions
			Outputs
				- bool: whether the selected offset can produce a valid board
		"""
		#initialise a queue
		q = Queue(unique=True)
		q.en_queue((5, 5))
		
		#initialize a set of found tiles
		found_tiles: set[TilePosition] = set()
		
		#while the queue is not empty
		while q.get_len() > 0:
			
			#get the next tile
			current_tile = q.de_queue()
			
			#add it to seen tiles
			found_tiles.add(current_tile)
			
			#add all "adjacent" tiles to the queue
			for tile in self._get_adjacent_tiles(current_tile, directions):
				if tile not in found_tiles:
					q.en_queue(tile)
		
		#if it finds all the tiles
		if found_tiles == set((row, col) for row in range(10) for col in range(10)):
			
			#remove the notification
			if "Offset options cannot produce a complete board" in self._error_lines:
				self._error_lines.remove("Offset options cannot produce a complete board")
				self._error_count -= 1
				self._object_controller.update_error_box(self._error_lines)
			return True
		
		#else notify the user
		if "Offset options cannot produce a complete board" not in self._error_lines:
			self._error_lines.add("Offset options cannot produce a complete board")
			self._error_count += 1
		self._object_controller.update_error_box(self._error_lines)
		return False
	
	def set_error_text(self, new_text_set: set[str] = None) -> None:
		#reset the error text
		if new_text_set is None:
			self._error_lines = set()
		else:
			self._error_lines = new_text_set
		self._error_count = len(self._error_lines)
	
	def get_error(self) -> bool:
		return self._error_count > 0
	
	#validation for the user login
	def validate_login(self, inpt_username: str, inpt_password: str) -> bool:
		"""
			Checks whether the username and password match one of the usernames and passwords in the database
			
			Inputs:
				- inpt_username: the username the user input
				- inpt_password: the password the user input
			Outputs
				- bool: whether the user successfully logs in
		
		"""
		
		#gets all the usernames
		self.cursor.execute(f"SELECT username FROM user WHERE username='{inpt_username}';")
		usernames = self.cursor.fetchall()
		
		#if there are any items in usernames, then there is a username that exists that matches the input username
		if len(usernames) >= 1:
			
			#get all passwords from that username that match the password
			self.cursor.execute(f"SELECT password FROM user WHERE password='{inpt_password}' AND username='{inpt_username}';")
			passwords = self.cursor.fetchall()
			
			#if there are any passwords, then the password matches
			if len(passwords) == 1:
				#get the user id
				self.cursor.execute(f"SELECT user_id FROM user WHERE password='{inpt_password}' AND username='{inpt_username}';")
				self.user_id = self.cursor.fetchall()[0][0]
				
				#log the user in
				self.cursor.execute(f"UPDATE user SET logged_in={True} WHERE user_id={self.user_id};")
				
				# remove the notification
				if "Invalid username or password" in self._error_lines:
					self._error_lines.remove("Invalid username or password")
					self._error_count -= 1
					self._object_controller.update_login_error_box(self._error_lines, "login")
				
				#return the fact that the user successfully logged in
				return True
		
		# else notify the user
		if "Invalid username or password" not in self._error_lines:
			self._error_count += 1
			self._error_lines.add("Invalid username or password")
		self._object_controller.update_login_error_box(self._error_lines, "login")
		
		# return the fact that the user failed to log in
		return False
	
	def create_account(self, username: str,
					   password: str,
					   password_confirmed: str,
					   music_volume: float,
					   sfx_volume: float,
					   chording: bool,
					   theme: str,
					   dig: int,
					   flag: int) -> bool:
		"""
			Validates account details and creates a new account
			
			Inputs:
				- username: the new username
				- password: the new password
				- password_confirmed: to get the user to confirm their password to make sure they are happy with it
		"""
		
		#if username or password is blank
		if username == "" or password == "":
			#notify the user
			if "Username or password is blank" not in self._error_lines:
				self._error_count += 1
				self._error_lines.add("Username or password is blank")
			self._object_controller.update_login_error_box(self._error_lines, "create_account")
			return False
		
		#else remove it from the error messages
		elif "Username or password is blank" in self._error_lines:
			self._error_lines.remove("Username or password is blank")
			self._error_count -= 1
			self._object_controller.update_login_error_box(self._error_lines, "create_account")
		
		#if the password matches their confirmation
		if password == password_confirmed:
			
			#remove it from the error strings
			if "Passwords are different" in self._error_lines:
				self._error_lines.remove("Passwords are different")
				self._error_count -= 1
				self._object_controller.update_login_error_box(self._error_lines, "create_account")
			
			#get all usernames that match the input username
			self.cursor.execute(f"SELECT username FROM user WHERE username='{username}';")
			username_list: list[tuple[str]] = self.cursor.fetchall()
			
			#if there aren't any, it is unique
			if len(username_list) == 0:
				
				#create a new account
				self.cursor.execute("INSERT INTO user (username, password, logged_in, custom_score, levels_score, keybinds, options) VALUES (?, ?, ?, ?, ?, ?, ?)",
									(username, password, True, 0, '{"Level 1":-1,"Level 2":-1,"Level 3":-1,"Level 4":-1,"Level 5":-1,"Level 6":-1}', '{"dig":-1,"flag":-2}', '{"chording":"true","theme":"Standard","music":0.8,"sfx":0.5}'))
				
				#update the user id
				self.cursor.execute(f"SELECT user_id FROM user WHERE username='{username}';")
				self.user_id = int(self.cursor.fetchall()[0][0])
				
				#set their options to the options they currently have active
				self.set_option(music_volume, "music")
				self.set_option(sfx_volume, "sfx")
				self.set_option(chording, "chording")
				self.set_option(theme, "theme")
				self.set_keybind("dig", dig)
				self.set_keybind("flag", flag)
				
				#remove it from the error strings
				if "Username already exists" in self._error_lines:
					self._error_lines.remove("Username already exists")
					self._error_count -= 1
					self._object_controller.update_login_error_box(self._error_lines, "create_account")
				return True
			else:
				# else notify the user
				if "Username already exists" not in self._error_lines:
					self._error_count += 1
					self._error_lines.add("Username already exists")
				self._object_controller.update_login_error_box(self._error_lines, "create_account")
		
		else:
			# else notify the user
			if "Passwords are different" not in self._error_lines:
				self._error_count += 1
				self._error_lines.add("Passwords are different")
			self._object_controller.update_login_error_box(self._error_lines, "create_account")
		
		return False
	
	def get_user_logged_in(self) -> bool:
		"""
			Checks if there is a user that has logged in, and set the current user id to be that user if there is.
		
			Inputs:
				- None
			Outputs:
				- bool, whether there is a logged-in user
		"""
		self.cursor.execute(f"SELECT user_id FROM user WHERE logged_in={True}")
		
		logged_in_user_list: list[tuple[int]] = self.cursor.fetchall()
		if len(logged_in_user_list) > 0:
			self.user_id = logged_in_user_list[0][0]
			return True
		else:
			self.user_id = None
		return False
	
	def get_user_id(self) -> int | None:
		return self.user_id
	
	def log_out(self) -> None:
		"""
			Log the user out, and set the ID to None
			
			Inputs:
				- None
			Outputs:
				- None
		"""
		self.cursor.execute(f"UPDATE user SET logged_in={False} WHERE user_id={self.user_id}")
		self.user_id = None
	
	def get_options(self) -> dict[str:bool]:
		"""
			Gets the options from the database, and converts them to a dictionary

			Inputs:
				- None
			Outputs:
				- None

		"""
		if self.user_id is None:
			return {"chording": True, "theme": "Standard", "music": 0.5, "sfx": 0.2}
		
		# gets the options from the database
		self.cursor.execute(f"SELECT options FROM user WHERE user_id={self.user_id}")
		options_string: str = self.cursor.fetchall()[0][0]
		
		# splits the items
		options_list: list[str] = options_string[1:-1].split(",")
		
		# splits the options into two separate items, and puts them into a list
		options_items: list[list[str]] = [keybind_item.split(":") for keybind_item in options_list]
		
		#initialize a list of values
		value_list = []
		
		#for each value
		for _, value in options_items:
			
			#if true, set to boolean True
			if value[1:-1].lower() == "true":
				value_list.append(True)
			# if false, set to boolean False
			elif value[1:-1].lower() == "false":
				value_list.append(False)
			else:
				try:
					#check if it can be parsed as a float
					float(value)
				#if not, it is a string and capitalize
				except ValueError:
					value_list.append(value[1:-1].capitalize())
				#else convert to a float
				else:
					value_list.append(float(value))
		
		# converts the list into a dictionary
		options_dict: dict[str:bool | str] = {options_items[i][0][1:-1]: value_list[i] for i in range(len(value_list))}
		
		return options_dict
	
	def set_option(self, option_value: bool | str | float, option_name: str) -> None:
		"""
			Sets a new option, or modifies an old one, such that options save when a user closes the game.

			Inputs:
				- option_name: the name of the event to change the keybind for
				- option_value: the boolean value to change the option to
			Outputs:
				- None
		"""
		if self.user_id is None:
			return
		
		if type(option_value) == float:
			self.cursor.execute(f"UPDATE user SET options = json_set(options, '$.{option_name}', {option_value}) WHERE user_id={self.user_id};")
		else:
			self.cursor.execute(f"UPDATE user SET options = json_set(options, '$.{option_name}', '{option_value}') WHERE user_id={self.user_id};")
	
	def set_keybind(self, event_name: str, key_value: int) -> None:
		"""
			Sets a new keybind, or modifies an old one, such that keybinds save when a user closes the game.

			Inputs:
				- event_name: the name of the event to change the keybind for
				- key_value: the integer value of the key to rebind it to
			Outputs:
				- None
		"""
		self.cursor.execute(f"UPDATE user SET keybinds = json_set(keybinds, '$.{event_name}', {key_value}) WHERE user_id={self.user_id};")
	
	def get_keybinds(self) -> dict[str:int]:
		"""
			Gets the keybinds from the database, and converts them to a dictionary
			
			Inputs:
				- None
			Outputs:
				- dict: the dictionary of keybinds
		
		"""
		#if user not logged in
		if self.user_id is None:
			return {"dig": -1, "flag": -2}
		
		#gets the keybinds from the database
		self.cursor.execute(f"SELECT keybinds FROM user WHERE user_id={self.user_id}")
		keybind_string: str = self.cursor.fetchall()[0][0]
		
		#splits the items
		keybind_list: list[str] = keybind_string[1:-1].split(",")
		
		#splits the keybinds into two separate items, and puts them into a list
		keybind_items: list[list[str]] = [keybind_item.split(":") for keybind_item in keybind_list]
		
		#converts the list into a dictionary
		keybind_dict: dict[str:int] = {event_name[1:-1]: int(key_value) for event_name, key_value in keybind_items}
		
		return keybind_dict
	
	def get_score(self) -> int:
		"""
			Gets the user's score from the database
			
			Inputs:
				- None
			Outputs:
				int: the user's score
		"""
		self.cursor.execute(f"SELECT custom_score FROM user WHERE user_id={self.user_id}")
		return int(self.cursor.fetchall()[0][0])
	
	def get_level_times(self) -> dict[str:int]:
		"""
			Gets and converts the dictionary of level times from the database
			
			Inputs:
				- None
			Outputs:
				- dict: the dictionary of level times
		"""
		if self.user_id is None:
			return {"Level 1": -1, "Level 2": -1, "Level 3": -1, "Level 4": -1, "Level 5": -1, "Level 6": -1}
		
		self.cursor.execute(f"SELECT levels_score FROM user WHERE user_id={self.user_id};")
		time_string: str = self.cursor.fetchall()[0][0]
		
		# splits the items
		time_list: list[str] = time_string[1:-1].split(",")
		
		# splits the times into two separate items, and puts them into a list
		time_items: list[list[str]] = [time_item.split(":") for time_item in time_list]
		
		# converts the list into a dictionary
		return {event_name[1:-1]: float(time_value) for event_name, time_value in time_items}
	
	def update_win(self, score: int) -> None:
		if self.user_id is None:
			return
		custom_score = self.get_score()
		if score > custom_score:
			self.cursor.execute(f"UPDATE user SET custom_score={score} WHERE user_id={self.user_id};")
	
	def update_level_win(self, level: int, time: float) -> None:
		"""
			Updates the time of the input level if it is a new fastest time
			
			Inputs:
				- level: the desired level to change
				- time: the new time
			Outputs:
				- None
		"""
		if self.user_id is None:
			return
		
		#get the dictionary of level times
		time_dict: dict[str:int] = self.get_level_times()
		
		#stores the name of the level
		level_name = f"Level {level}"
		
		#if the new time is better than the old, update it
		if time_dict[level_name] > time or time_dict[level_name] == -1:
			self.cursor.execute(f"UPDATE user SET levels_score = json_set(levels_score, '$.{level_name}', {time}) WHERE user_id={self.user_id};")
	
	def close_connection(self) -> None:
		self.connection.commit()
		self.connection.close()