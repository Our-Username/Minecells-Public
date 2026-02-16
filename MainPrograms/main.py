import math
import os
import string
import sys
import time
import pygame
import multiprocessing as mp
from queue import Empty
from pygame import Surface, font
from typing import Type, TypeVar

from BoardGenHub import BoardGenHub
from MainPrograms.GameplayAlgorithms import resolve_left_click, resolve_right_click, resolve_left_click_offset
from MainPrograms.ObjectClasses.KeybindBox import KeybindBox
from MainPrograms.ObjectClasses.Levels import LevelManager
from MainPrograms.ObjectClasses.ObjectControl import ObjectControl
from MainPrograms.ObjectClasses.TextInputBox import TextInputBox
from MainPrograms.ObjectClasses.BoundingBox import BoundingBox
from MainPrograms.ObjectClasses.Tile import Tile
from MainPrograms.ObjectClasses.Validation import Validation

type Board = list[list[int]]
type Coordinate = tuple[float, float]
type Colour = tuple[int, int, int]
type TilePosition = tuple[int, int]
ClassVariable = TypeVar("ClassVariable")


class MainProgram:
	def __init__(self, surface: Surface, text_font: font.Font, tile_font: font.Font, fps: int = 60) -> None:
		"""
			Constructor class for the MainProgram class
			
			Inputs:
				- surface: the WIN surface
				- text_font: the font to be used by the text informing the user
				- tile_font: the font to be used by the tiles
				- fps: the frame rate to be used by the system (60 by default)
			Initializes:
				- self._WIN: the WIN surface
				- self.WIDTH: the width of the WIN surface
				- self.HEIGHT: the height of the WIN surface
				- self.POINT_SIZE: the point unit to ensure that the screen scales to any screen dimensions
				- self.FONT: the font to be used by the text informing the user
				- self.TILE_FONT: the font to be used by the tiles
				- self.FPS: the frame rate to be used by the system (60 by default)
				- self._object_controller: an instance of the class that controls the physical objects
				- Other variables initialized in self.main, which have to be initialized here
		"""
		
		#Initialise main attribute variables
		self.WIN: Surface = surface
		self.WIDTH: int = surface.get_width()
		self.HEIGHT: int = surface.get_height()
		self.POINT_SIZE: float = self.WIDTH / 200
		self.FONT: font.Font = text_font
		self.TILE_FONT: font.Font = tile_font
		self.FPS: int = fps
		self._object_controller: ObjectControl = ObjectControl(self, WIN, FONT, TILE_FONT, TEXTBOX_FONT, TEXTBOX_FONT_2, TIME_FONT, fps)
		self.board_gen_hub: BoardGenHub = BoardGenHub()
		self.validator: Validation = Validation(self._object_controller)
		self.level_manager: LevelManager = LevelManager()
		self.colour_dict: dict[str:Colour] = self._object_controller.get_colour_dict(self.validator.get_options()["theme"])
		
		#Initialize self.main variables
		self.board: list[list[int]] = []
		self.revealed_tiles: set[TilePosition] | None = set()
		self.public_board: list[list[int]] = []
		self.minecount: int = 0
		self.start_minecount: int = 0
		self.board_rows: int = 0
		self.board_cols: int = 0
		self.spaces: int = 0
		self.difficulty: int = 0
		self.seed: str = ""
		self.screen: str = ""
		self.start_active: bool = False
		self.gameplay_active: bool = False
		self._run: bool = True
		self._ready: bool = True
		self.start_time: float = 0
		self._shift_active: bool = False
		self.generator: str = ""
		self.offset_directions: list[tuple[int, int]] = []
		self.offset_active: bool = False
		self.tile_surface: Surface | None = None
		self.zoomed_tile_surface: Surface | None = None
		self.tile_surface_dims: tuple[float, float] = (10 * self.board_cols * self.POINT_SIZE, 10 * self.board_rows * self.POINT_SIZE)
		self.tile_surface_zoom: float = 1
		self.tile_surface_offset: tuple[float, float] = (-1 * 60 * self.POINT_SIZE, -1 * 25 * self.POINT_SIZE)
		self.alive: bool = False
		self.won: bool = False
		self.finish_time: float = 0
		self.valid_minecount: bool = False
		self.valid_rows: bool = False
		self.valid_cols: bool = False
		self.valid_difficulty: bool = False
		self.valid_offset: bool = False
		self.username: str = ""
		self.password: str = ""
		self.password_confirmed: str = ""
		self.valid_login: bool = False
		self.keybind_dict: dict[str:int] = self.validator.get_keybinds()
		self.chording: bool = self.validator.get_options()["chording"]
		self.theme: str = "Standard"
		self.current_level: int = 1
		self.zoom_animation_count: int = 0
		self.zoom_animation_multiplier: float = 0
		self.zoom_animation_centre: Coordinate = (0, 0)
		
		#multiprocessing variables
		self.workers: list[mp.Process] = []
		self.task_queue: mp.Queue | None = None
		self.result_queue: mp.Queue | None = None
		
		#music variables
		self.music_volume: float = self.validator.get_options()["music"]
		self.sfx_volume: float = self.validator.get_options()["sfx"]
		self.quieten_active: bool = False
	
	@staticmethod
	def create_object(object_class: Type[ClassVariable], position: Coordinate, *args) -> ClassVariable:
		"""
			Create an object
			
			Inputs:
				- object_class: the class to create the object from
				- position: the position the object is to be drawn at
				- *args: the object arguments
			Outputs:
				- object_created: the instance of the object created
		
		"""
		object_created: object = object_class(*args)
		object_created.set_pos(position)
		object_created.draw()
		
		return object_created
	
	@staticmethod
	def clear_queue(queue: mp.Queue) -> None:
		"""
			Empties a multiprocessing queue

			Inputs:
				- queue: the queue to empty
			Outputs:
				- None
		"""
		try:
			#while there are still items in the queue
			while True:
				#remove the next item
				queue.get_nowait()
		except Empty:
			#stop if empty
			pass
	
	def get_current_minecount(self, board: Board) -> int:
		"""
			Gets the current minecount as it would be displayed to the user

			Inputs:
				- board: the board to work on
			Returns:
				- count: the current minecount
		"""
		count = 0  # initialize minecount
		
		for col in range(self.board_cols):
			for row in range(self.board_rows):  # for each tile
				if board[row][col] == -1:  # if tile is flag, decrement minecount
					count += 1
		
		return count
	
	def _set_spaces(self, width, height) -> None:
		"""
			Update all the tiles that are space tiles, and update the public board accordingly
			
			Inputs:
				- width: the width of the board
				- height: the height of the board
			Modifies:
				- self.public_board: the public board the user can see
		"""
		
		#for each item in the board
		for row in range(height):
			for col in range(width):
				
				#if it is a space
				if self.board[row][col] == -3:
					#set its public value to -3
					self.public_board[row][col] = -3
					
					#set its colour to the space colour
					self._object_controller.tile_board[row][col].fill(self.colour_dict["Space"])
	
	@staticmethod
	def set_int_variable(var: str) -> int:
		"""
			Converts a string from a textbox into an integer, default 0
			
			Inputs:
				- var: the variable to convert
			Outputs:
				- var: the converted variable
		"""
		if var == "":
			return 0
		else:
			return int(var)
	
	def start_game(self, start_position: TilePosition) -> None:
		"""
			Starts the game after the first click
			
			Inputs:
				- start_position: the position the user clicked
			Outputs:
				- None
		"""
		
		# set the minecount to what the user input
		self.minecount = self.set_int_variable(self._object_controller.text_box_dict[("minecount", "generator_select")].get_text())
		self.start_minecount = self.minecount
		
		#generate a public board which represents what the user can see
		self.public_board = [[-2 for _ in range(self.board_cols)] for _ in range(self.board_rows)]
		
		self.start_active = False
		
		#if an offset puzzle board is being generated
		match self.generator.lower():
			case "offset puzzle":
				
				#get the generated board
				self.board, self.revealed_tiles = self.result_queue.get()
				
				#if there is no board generated
				if self.revealed_tiles is None:
					# clear the queues to get rid of any old boards
					self.clear_queue(self.task_queue)
					self.clear_queue(self.result_queue)
					
					# for all cores
					for i in range(mp.cpu_count()):
						# generate a board
						self.task_queue.put((self.board_gen_hub.gen_board_parallel, self.generator, self.board_cols, self.board_rows, self.minecount, self.seed, self.spaces, self.difficulty, self.offset_directions))
					
					# get the generated board
					self.board, self.revealed_tiles = self.result_queue.get()
				
				# update the public board with the revealed tiles
				for row, col in self.revealed_tiles:
					self.public_board[row][col] = self.board[row][col]
					self._object_controller.tile_board[row][col].set_text(str(self.board[row][col]), self.TILE_FONT)
					self._object_controller.tile_board[row][col].set_value(self.board[row][col])
			
			#if it is a puzzle style board
			case "puzzle":
				
				# get the generated board
				self.board, self.revealed_tiles = self.result_queue.get()
				
				# if there is no board generated
				if self.revealed_tiles is None:
					# clear the queues to get rid of any old boards
					self.clear_queue(self.task_queue)
					self.clear_queue(self.result_queue)
					
					# for all cores
					for i in range(mp.cpu_count()):
						# generate a board
						self.task_queue.put((self.board_gen_hub.gen_board_parallel, self.generator, self.board_cols, self.board_rows, self.minecount, self.seed, self.spaces, self.difficulty))
					
					# get the generated board
					self.board, self.revealed_tiles = self.result_queue.get()
				
				# update the public board with the revealed tiles
				for row, col in self.revealed_tiles:
					self.public_board[row][col] = self.board[row][col]
					self._object_controller.tile_board[row][col].set_text(str(self.board[row][col]), self.TILE_FONT)
					self._object_controller.tile_board[row][col].set_value(self.board[row][col])
			
			case "offset":
				
				# clear the queues to get rid of any old boards
				self.clear_queue(self.task_queue)
				self.clear_queue(self.result_queue)
				
				# for all cores
				for i in range(mp.cpu_count()):
					# generate a board
					self.task_queue.put((self.board_gen_hub.gen_board_parallel, self.generator, self.board_cols, self.board_rows, start_position, self.minecount, self.seed, self.spaces, self.offset_directions))
				
				# get the generated board
				self.board, self.revealed_tiles = self.result_queue.get()
			
			case "space":
				
				# clear the queues to get rid of any old boards
				self.clear_queue(self.task_queue)
				self.clear_queue(self.result_queue)
				
				# for all cores
				for i in range(mp.cpu_count()):
					# generate a board
					self.task_queue.put((self.board_gen_hub.gen_board_parallel, self.generator, self.board_cols, self.board_rows, start_position, self.minecount, self.seed, self.spaces))
				
				# get the generated board
				self.board, self.revealed_tiles = self.result_queue.get()
			
			#if a standard board is being produced
			case _:
				
				# clear the queues to get rid of any old boards
				self.clear_queue(self.task_queue)
				self.clear_queue(self.result_queue)
				
				# for all cores
				for i in range(mp.cpu_count()):
					# generate a board
					self.task_queue.put((self.board_gen_hub.gen_board_parallel, self.generator, self.board_cols, self.board_rows, start_position, self.minecount, self.seed, i))
				
				self.board, self.revealed_tiles = self.result_queue.get()
				
				# get the generated board
				while self.board[start_position[0]][start_position[1]] != 0:
					# clear the queues to get rid of any old boards
					self.clear_queue(self.task_queue)
					self.clear_queue(self.result_queue)
					
					# for all cores
					for i in range(mp.cpu_count()):
						# generate a board
						self.task_queue.put((self.board_gen_hub.gen_board_parallel, self.generator, self.board_cols, self.board_rows, start_position, self.minecount, self.seed, i))
					
					self.board, self.revealed_tiles = self.result_queue.get()
		
		# update the public board with the spaces
		self._set_spaces(self.board_cols, self.board_rows)
		
		#hides any displayed text
		text_cover = self.create_object(BoundingBox,
										(70 * self.POINT_SIZE, 15 * self.POINT_SIZE),
										self.WIN, (60 * self.POINT_SIZE), (10 * self.POINT_SIZE), self.POINT_SIZE, self.colour_dict["Background"], 0)
		text_cover.update()
		
		#if zoomed out, initialize the zoom in animation
		if self.tile_surface_zoom < 1 and "puzzle" not in self.generator.lower():
			self.zoom_animation_count = 10
			self.zoom_animation_multiplier = (1 / self.tile_surface_zoom) ** (1 / self.zoom_animation_count)
			self.zoom_animation_centre = pygame.mouse.get_pos()
		
		#start the game
		self._object_controller.start_game(self.minecount)
		
		#digs the tile if it is not a puzzle
		if "puzzle" not in self.generator.lower():
			
			# adapt for non offset boards
			if "offset" not in self.generator.lower():
				dirs = [(x, y) for x in [-1, 0, 1] for y in [-1, 0, 1]]
				dirs.remove((0, 0))
			else:
				dirs: list[TilePosition] = self.offset_directions
			
			#complete a left click on the start position
			self.alive, self.won = resolve_left_click(self.public_board, self.board, self._object_controller.tile_board, start_position, self.WIN, dirs, self.colour_dict, self.sfx_volume, False)
			
			#set gameplay active to whether the game is ongoing
			self.gameplay_active = self.alive and not self.won
			
			#if there is no zoomed surface, display the default
			if self.zoomed_tile_surface is None:
				self.WIN.blit(self.tile_surface, (-self.tile_surface_offset[0], -self.tile_surface_offset[1]))
			#else display the zoomed surface
			else:
				self.WIN.blit(self.zoomed_tile_surface, (-self.tile_surface_offset[0], -self.tile_surface_offset[1]))
			
			#redraw the gameplay screen
			self._object_controller.redraw_gameplay_screen()
		
		#for a puzzle board
		else:
			
			#user is alive and hasn't won
			self.alive = True
			self.won = False
			
			#gameplay is active
			self.gameplay_active = True
			
			# if there is no zoomed surface, display the default
			if self.zoomed_tile_surface is None:
				self.WIN.blit(self.tile_surface, (-self.tile_surface_offset[0], -self.tile_surface_offset[1]))
			# else display the zoomed surface
			else:
				self.WIN.blit(self.zoomed_tile_surface, (-self.tile_surface_offset[0], -self.tile_surface_offset[1]))
			
			# redraw the gameplay screen
			self._object_controller.redraw_gameplay_screen()
	
	def init_game(self, ready: bool = False) -> None:
		"""
			Sets the game up so that the user can click the first tile
			
			Inputs:
				- ready: whether the click should go through immediately as the user clicks or not
			Outputs:
				- None
		"""
		
		#sets the mode such that the main loop knows that it is in this state
		self._ready = ready
		self.start_active = True
		self.gameplay_active = False
		self.won = False
		
		self._object_controller.init_game()
	
	def close_game(self) -> None:
		"""
			Function to be passed as a parameter for the on_click for the exit button
			so that it can modify the run variable directly
			
			Inputs:
				None
			Outputs:
				None
		"""
		self._run = False
	
	def gameplay_left_click(self, mouse_pos: Coordinate) -> None:
		"""
			Events that happen when the screen type is gameplay and the user does a left click

			Inputs:
				- mouse_pos: the position of the mouse
			Outputs:
				None

		"""
		# if waiting for user to click first tile
		if self.start_active and self._ready and not self.gameplay_active:
			tile: TilePosition | None = self._object_controller.check_tile_clicked(self._object_controller.tile_board, mouse_pos, self.tile_surface_zoom, self.tile_surface_offset)
			
			# if a tile was clicked
			if tile is not None:
				# start the game
				start_pos: TilePosition = tile
				self.start_active = False
				self.gameplay_active = True
				self.start_time = time.perf_counter()
				self.start_game(start_pos)
		
		# if the game is running
		if self.gameplay_active and self._ready and not self.start_active:
			
			# get the tile that the user clicked
			tile: TilePosition | None = self._object_controller.check_tile_clicked(self._object_controller.tile_board, mouse_pos, self.tile_surface_zoom, self.tile_surface_offset)
			
			# if a tile was clicked
			if tile is not None:
				
				#adapt for offset
				if "offset" not in self.generator.lower():
					dirs = [(x, y) for x in [-1, 0, 1] for y in [-1, 0, 1]]
					dirs.remove((0, 0))
				else:
					dirs: list[TilePosition] = self.offset_directions
				
				# dig the tile
				self.alive, self.won = resolve_left_click(self.public_board, self.board,
														  self._object_controller.tile_board, tile,
														  self.WIN, dirs, self.colour_dict, self.sfx_volume,
														  self.chording, "puzzle" in self.generator)
				
				#if the game has finished
				if not self.alive and self.gameplay_active:
					self.finish_time = time.perf_counter() - self.start_time
				
				self.gameplay_active = self.alive and not self.won
				
				#if the game has been won
				if self.won:
					self.on_win()
				
				# if there is no zoomed surface, display the default
				if self.zoomed_tile_surface is None:
					self.WIN.blit(self.tile_surface, (-self.tile_surface_offset[0], -self.tile_surface_offset[1]))
				# else display the zoomed surface
				else:
					#redraw the zoomed surface
					self.zoomed_tile_surface = pygame.transform.smoothscale(self.tile_surface,
																			(self.tile_surface_dims[0] * self.tile_surface_zoom, self.tile_surface_dims[1] * self.tile_surface_zoom))
					self.WIN.blit(self.zoomed_tile_surface, (-self.tile_surface_offset[0], -self.tile_surface_offset[1]))
				
				# redraw the gameplay screen
				self._object_controller.redraw_gameplay_screen()
		self._ready = True
	
	def tutorial_left_click(self, mouse_pos: Coordinate) -> None:
		"""
			Events which occur when the user makes a left click on the tutorial screen
			
			Inputs:
				- mouse_pos: the position of the mouse on the screen
			Outputs:
				- None
		"""
		
		# prevents the user from instantly clicking on entering the screen
		if self._ready:
			
			# initializes the sublevel count list
			# this contains the number of sublevels in each level
			sublevel_count_list: list[int] = [3, 2, 1, 1, 2, 3, 1, 1, 1, 1]
			
			if sublevel_count_list[self.current_level - 1] == 3:
				#gets the sublevel from the position of the mouse on the screen
				if mouse_pos[0] < self.WIDTH / 3:
					sublevel = 1
				elif mouse_pos[0] < 2 * self.WIDTH / 3:
					sublevel = 2
				else:
					sublevel = 3
			
			elif sublevel_count_list[self.current_level - 1] == 2:
				# gets the sublevel from the position of the mouse on the screen
				if mouse_pos[0] < self.WIDTH / 2:
					sublevel = 1
				else:
					sublevel = 2
			else:
				sublevel = 1
			
			#gets the tile board from the dictionary
			board: list[list[Tile]] = self._object_controller.tutorial_board_dict[(self.current_level, sublevel)][0]
			
			# get the tile that the user clicked
			tile: TilePosition | None = self._object_controller.check_tile_clicked(board, mouse_pos, 1, (0, 0))
			
			# if a tile was clicked
			if tile is not None:
				tile_board, private_board, public_board = self._object_controller.tutorial_board_dict[(self.current_level, sublevel)]
				
				#store the directions of adjacent tiles
				dirs = [(x, y) for x in [-1, 0, 1] for y in [-1, 0, 1]]
				dirs.remove((0, 0))
				
				# dig the tile
				resolve_left_click(public_board, private_board, tile_board, tile,
								   self.WIN, dirs, self.colour_dict, self.sfx_volume,
								   tutorial=True)
				
				#updates the boards in the dictionary
				self._object_controller.tutorial_board_dict[(self.current_level, sublevel)] = tile_board, private_board, public_board
		
		# allow the user to click buttons (avoid the user from accidentally instantly starting as it carries on the click from the start button)
		self._ready = True
	
	def tutorial_right_click(self, mouse_pos: Coordinate) -> None:
		"""
			Events which occur when the user makes a right click on the tutorial screen

			Inputs:
				- mouse_pos: the position of the mouse on the screen
			Outputs:
				- None
		"""
		
		# initializes the sublevel count list
		#this contains the number of sublevels in each level
		sublevel_count_list: list[int] = [3, 2, 1, 1, 2, 3, 1, 1, 1, 1]
		
		if sublevel_count_list[self.current_level - 1] == 3:
			# gets the sublevel from the position of the mouse on the screen
			if mouse_pos[0] < self.WIDTH / 3:
				sublevel = 1
			elif mouse_pos[0] < 2 * self.WIDTH / 3:
				sublevel = 2
			else:
				sublevel = 3
		
		elif sublevel_count_list[self.current_level - 1] == 2:
			# gets the sublevel from the position of the mouse on the screen
			if mouse_pos[0] < self.WIDTH / 2:
				sublevel = 1
			else:
				sublevel = 2
		else:
			sublevel = 1
		
		# gets the tile board from the dictionary
		board: list[list[Tile]] = self._object_controller.tutorial_board_dict[(self.current_level, sublevel)][0]
		
		# get the tile that the user clicked
		tile: TilePosition | None = self._object_controller.check_tile_clicked(board, mouse_pos, 1, (0, 0))
		
		# if a tile was clicked
		if tile is not None:
			tile_board, private_board, public_board = self._object_controller.tutorial_board_dict[(self.current_level, sublevel)]
			
			# flag the tile
			resolve_right_click(public_board, tile_board, tile,
								BoundingBox(WIN, self.WIDTH, self.HEIGHT, self.POINT_SIZE, (0, 0, 0), 2),
								self.minecount, BoundingBox(WIN, self.WIDTH, self.HEIGHT, self.POINT_SIZE, (0, 0, 0), 2),
								self.colour_dict, self.sfx_volume, tutorial=True)
			
			# updates the boards in the dictionary
			self._object_controller.tutorial_board_dict[(self.current_level, sublevel)] = tile_board, private_board, public_board
	
	def on_win(self) -> None:
		"""
			Code to execute once the game has been one
			
			Inputs:
				- None
			Outputs:
				- None
		"""
		
		self.music_volume = 1
		
		#calculate time taken between the finish and now
		self.finish_time = time.perf_counter() - self.start_time
		
		#set a multiplier to equal 3^(15 * mine density)
		multiplier = 2 ** (15 * self.start_minecount / (self.board_rows * self.board_cols))
		
		if self.chording:
			multiplier *= max(1 / math.log10(self.start_minecount), 1)
		
		#set the score to equal the multiplier multiplied by the minecount divided by a function of time
		score = int(multiplier * self.start_minecount / max(0.1, math.log10(self.finish_time)))
		
		#update the win in the database
		if "level" in self.seed.lower():
			self.validator.update_level_win(int(self.seed[-1]), round(self.finish_time, 2))
		else:
			self.validator.update_win(score)
		
		#auto completes flags
		self.minecount = self._object_controller.on_win(self.public_board, self.board, self.minecount)
	
	def gameplay_right_click(self, mouse_pos: Coordinate) -> None:
		"""
			Events that happen when the screen type is gameplay and the user does a right click

			Inputs:
				- mouse_pos: the position of the mouse
			Outputs:
				None

		"""
		# if the game is running
		if self.gameplay_active:
			
			# get the tile that the user clicked
			tile: TilePosition | None = self._object_controller.check_tile_clicked(self._object_controller.tile_board, mouse_pos, self.tile_surface_zoom, self.tile_surface_offset)
			
			# if a tile was clicked
			if tile is not None:
				# flag the tile
				self.minecount = resolve_right_click(self.public_board, self._object_controller.tile_board,
													 tile, self._object_controller.box_dict[("board_box", "gameplay")],
													 self.minecount, self._object_controller.box_dict[("minecount_box", "gameplay")],
													 self.colour_dict, self.sfx_volume)
				
				# if there is no zoomed surface, display the default
				if self.zoomed_tile_surface is None:
					self.WIN.blit(self.tile_surface, (-self.tile_surface_offset[0], -self.tile_surface_offset[1]))
				# else display the zoomed surface
				else:
					# redraw the zoomed surface
					self.zoomed_tile_surface = pygame.transform.smoothscale(self.tile_surface,
																			(self.tile_surface_dims[0] * self.tile_surface_zoom, self.tile_surface_dims[1] * self.tile_surface_zoom))
					self.WIN.blit(self.zoomed_tile_surface, (-self.tile_surface_offset[0], -self.tile_surface_offset[1]))
				
				# redraw the gameplay screen
				self._object_controller.redraw_gameplay_screen()
	
	def generate_board_early(self) -> None:
		match self.generator.lower():
			
			# if an offset puzzle board is being generated
			case "offset puzzle":
				
				# if all the parameters are valid
				if self.valid_cols == self.valid_rows == self.valid_difficulty == self.valid_minecount == self.valid_offset == True:
					
					# clear the queues to get rid of any old boards
					self.clear_queue(self.task_queue)
					self.clear_queue(self.result_queue)
					
					# for all cores
					for i in range(mp.cpu_count()):
						# generate a board
						self.task_queue.put((self.board_gen_hub.gen_board_parallel, self.generator, self.board_cols, self.board_rows, self.minecount, self.seed, self.spaces, self.difficulty, self.offset_directions))
			
			# if it is a puzzle style board
			case "puzzle":
				
				# if all the parameters are valid
				if self.valid_cols == self.valid_rows == self.valid_difficulty == self.valid_minecount == True:
					
					# clear the queues to get rid of any old boards
					self.clear_queue(self.task_queue)
					self.clear_queue(self.result_queue)
					
					# for all cores
					for i in range(mp.cpu_count()):
						# generate a board
						self.task_queue.put((self.board_gen_hub.gen_board_parallel, self.generator, self.board_cols, self.board_rows, self.minecount, self.seed, self.spaces, self.difficulty))
	
	def generator_select_keydown(self, key: str) -> None:
		"""
			Events that happen when the screen type is generator_select and the user presses a key

			Inputs:
				- key: the key pressed
			Outputs:
				None

		"""
		
		# sets the type of the text box and target text box for ease of use
		text_box: TextInputBox
		target_text_box: TextInputBox | None = None
		
		#auto upper case if shift
		if self._shift_active:
			key = key.upper()
		
		#for each text box name
		for text_box_name in self._object_controller.text_box_dict.keys():
			
			# get the text box
			text_box = self._object_controller.text_box_dict[text_box_name]
			
			#if the text box is focused, save the text box and break
			if text_box.get_focused():
				target_text_box = text_box
				break
		
		#if text box is focused
		if target_text_box is not None:
			match target_text_box.get_name():
				case "seed":
					
					# if within the character limit and is short
					if len(target_text_box.get_text()) < 4:
						# update and display its text
						target_text_box.add_char(key)
						target_text_box.update()
						target_text_box.display_text(TEXTBOX_FONT, self.colour_dict["Text"])
					
					#if within the character limit
					elif len(target_text_box.get_text()) < 10:
						#update and display its text
						target_text_box.add_char(key)
						target_text_box.update()
						target_text_box.display_text(TEXTBOX_FONT_2, self.colour_dict["Text"])
				
				# if minecount is focused
				case "minecount" | "spaces":
					
					# if within the character limit
					if len(target_text_box.get_text()) < 4 and key in string.digits:
						# update and display its text
						target_text_box.add_char(key)
						target_text_box.update()
						target_text_box.display_text(TEXTBOX_FONT, self.colour_dict["Text"])
						minecount: int = self.set_int_variable(self._object_controller.text_box_dict[("minecount", "generator_select")].get_text())
						spaces: int = self.set_int_variable(self._object_controller.text_box_dict[("spaces", "generator_select")].get_text())
						
						# make the generator default "Standard"
						if self.generator == "":
							self.generator = "Standard"
						
						#validate the minecount
						self.valid_minecount = self.validator.minecount(minecount, self.board_rows, self.board_cols, self.board_rows * self.board_cols, spaces, self.generator)
						
						#set the minecount and the spaces
						self.minecount = minecount
						self.spaces = spaces
				
				# if rows/cols is focused
				case "rows" | "cols":
					
					# if within the character limit
					if len(target_text_box.get_text()) < 2 and key in string.digits:
						# update and display its text
						target_text_box.add_char(key)
						target_text_box.update()
						target_text_box.display_text(TEXTBOX_FONT, self.colour_dict["Text"])
						
						#store the old area of the board
						old_area = self.board_rows * self.board_cols
						
						# get the rows and columns
						rows = self.set_int_variable(self._object_controller.text_box_dict[("rows", "generator_select")].get_text())
						cols = self.set_int_variable(self._object_controller.text_box_dict[("cols", "generator_select")].get_text())
						
						#if the name of the box is rows
						if target_text_box.get_name() == "rows":
							
							#validate the rows
							self.valid_rows = self.validator.rows(rows, cols)
							self.board_rows = rows
						
						# if the name of the box is cols
						elif target_text_box.get_name() == "cols":
							
							# validate the rows
							self.valid_cols = self.validator.cols(rows, cols)
							self.board_cols = cols
						
						#get the minecount and spaces
						minecount: int = self.set_int_variable(self._object_controller.text_box_dict[("minecount", "generator_select")].get_text())
						spaces: int = self.set_int_variable(self._object_controller.text_box_dict[("spaces", "generator_select")].get_text())
						
						#re-validate the minecount
						self.valid_minecount = self.validator.minecount(minecount, self.board_rows, self.board_cols, old_area, spaces, self.generator)
				
				#if the box is difficulty
				case "difficulty":
					
					# if within the character limit
					if len(target_text_box.get_text()) == 0 and key in string.digits:
						# update and display its text
						target_text_box.add_char(key)
						target_text_box.update()
						target_text_box.display_text(TEXTBOX_FONT, self.colour_dict["Text"])
						
						# get the difficulty
						difficulty = self._object_controller.text_box_dict[("difficulty", "generator_select")].get_text()
						
						# difficulty 1 is the hardest (0 does not generate any revealed tiles so is impossible)
						if difficulty == "":
							difficulty = 1
						else:
							difficulty = int(difficulty)
						
						#revalidate the difficulty
						self.valid_difficulty = self.validator.difficulty(difficulty)
						self.difficulty = difficulty
			
			#check if the board can be generated early (if it is a puzzle or offset puzzle board)
			self.generate_board_early()
	
	def generator_select_backspace(self) -> None:
		"""
			Events that happen when the screen type is generator_select and the user presses backspace

			Inputs:
				None
			Outputs:
				None

		"""
		
		# sets the type of the text box and target text box for ease of use
		text_box: TextInputBox
		target_text_box: TextInputBox | None = None
		
		# for each text box name
		for text_box_name in self._object_controller.text_box_dict.keys():
			
			# get the text box
			text_box = self._object_controller.text_box_dict[text_box_name]
			
			# if the text box is focused, save the text box and break
			if text_box.get_focused():
				target_text_box = text_box
				break
		
		# if a text box is focused
		if target_text_box is not None:
			
			# if there are character to delete
			if len(target_text_box.get_text()) > 0:
				
				# update and display its text
				if len(target_text_box.get_text()) > 5:
					target_text_box.remove_char()
					target_text_box.update()
					target_text_box.display_text(TEXTBOX_FONT_2, self.colour_dict["Text"])
				else:
					target_text_box.remove_char()
					target_text_box.update()
					target_text_box.display_text(TEXTBOX_FONT, self.colour_dict["Text"])
				
				#check and compare the name of the box
				match target_text_box.get_name().lower():
					
					#if the seed text box is selected
					case "seed":
						
						#update the seed attribute
						self.seed = self._object_controller.text_box_dict[("seed", "generator_select")].get_text()
					
					#if the rows box is selected
					case "rows":
						
						old_area = self.board_rows * self.board_cols
						
						# get the columns
						rows = self.set_int_variable(self._object_controller.text_box_dict[("rows", "generator_select")].get_text())
						
						self.valid_rows = self.validator.rows(rows, self.board_cols)
						self.board_rows = rows
						
						# get the minecount and spaces
						minecount: int = self.set_int_variable(self._object_controller.text_box_dict[("minecount", "generator_select")].get_text())
						spaces: int = self.set_int_variable(self._object_controller.text_box_dict[("spaces", "generator_select")].get_text())
						
						# re-validate the minecount
						self.valid_minecount = self.validator.minecount(minecount, self.board_rows, self.board_cols, old_area, spaces, self.generator)
					
					#if the rows box is selected
					case "cols":
						
						old_area = self.board_rows * self.board_cols
						
						# get the rows
						cols = self.set_int_variable(self._object_controller.text_box_dict[("cols", "generator_select")].get_text())
						
						# validate the rows
						self.valid_cols = self.validator.cols(self.board_rows, cols)
						self.board_cols = cols
						
						# get the minecount and spaces
						minecount: int = self.set_int_variable(self._object_controller.text_box_dict[("minecount", "generator_select")].get_text())
						spaces: int = self.set_int_variable(self._object_controller.text_box_dict[("spaces", "generator_select")].get_text())
						
						# re-validate the minecount
						self.valid_minecount = self.validator.minecount(minecount, self.board_rows, self.board_cols, old_area, spaces, self.generator)
					
					#if the minecount or the space box is selected
					case "minecount" | "spaces":
						
						#get the minecount and space count
						minecount: int = self.set_int_variable(self._object_controller.text_box_dict[("minecount", "generator_select")].get_text())
						spaces: int = self.set_int_variable(self._object_controller.text_box_dict[("spaces", "generator_select")].get_text())
						
						# make the generator default "Standard"
						if self.generator == "":
							self.generator = "Standard"
						
						#validate the minecount
						self.valid_minecount = self.validator.minecount(minecount, self.board_rows, self.board_cols, self.board_rows * self.board_cols, spaces, self.generator)
						
						#update the minecount and spaces
						self.minecount = minecount
						self.spaces = spaces
					
					#if the difficulty box is selected
					case "difficulty":
						# get the difficulty
						difficulty = self._object_controller.text_box_dict[("difficulty", "generator_select")].get_text()
						
						# difficulty 1 is the hardest (0 does not generate any revealed tiles so is impossible)
						if difficulty == "":
							difficulty = 1
						else:
							difficulty = int(difficulty)
						
						self.valid_difficulty = self.validator.difficulty(difficulty)
						self.difficulty = difficulty
				
				self.generate_board_early()
	
	def offset_left_click(self, mouse_pos: Coordinate) -> None:
		offset_board = [[1 if (row - 2, col - 2) in self.offset_directions else 0 for col in range(5)] for row in range(5)]
		
		if self.offset_active and self._ready:
			# get the tile that the user clicked
			tile: TilePosition | None = self._object_controller.check_tile_clicked(self._object_controller.offset_tile_board, mouse_pos,
																				   1, (0, 0))
			
			# if a tile was clicked
			if tile not in [None, (2, 2)]:
				# flag the tile
				offset_board = resolve_left_click_offset(offset_board, self._object_controller.offset_tile_board,
														 tile, self._object_controller.box_dict[("board_box", "offset")], self.colour_dict)
				
				for row in range(5):
					for col in range(5):
						if offset_board[row][col] == 1 and (row - 2, col - 2) not in self.offset_directions:
							self.offset_directions.append((row - 2, col - 2))
						elif offset_board[row][col] == 0 and (row - 2, col - 2) in self.offset_directions:
							self.offset_directions.remove((row - 2, col - 2))
		self._ready = True
	
	def login_keydown(self, key: str) -> None:
		"""
			Events that happen when the screen type is login and the user presses a key

			Inputs:
				- key: the key pressed
			Outputs:
				None

		"""
		
		# sets the type of the text box and target text box for ease of use
		text_box: TextInputBox
		target_text_box: TextInputBox | None = None
		
		if self._shift_active:
			key = key.upper()
		
		# for each text box name
		for text_box_name in self._object_controller.text_box_dict.keys():
			
			# get the text box
			text_box = self._object_controller.text_box_dict[text_box_name]
			
			# if the text box is focused, save the text box and break
			if text_box.get_focused():
				target_text_box = text_box
				break
		
		# if text box is focused
		if target_text_box is not None:
			if self.screen == "login":
				match target_text_box.get_name().lower():
					case "username":
						
						# if within the character limit
						if len(target_text_box.get_text()) < 24:
							# update and display its text
							if key == "space":
								key = " "
							target_text_box.add_char(key)
							target_text_box.update()
							target_text_box.display_text(pygame.font.Font(resource_path("MainPrograms/Fonts/Roboto/static/Roboto-Bold.ttf"), int(POINT_SIZE * min(6.0, 7 - math.log2(0.75 * len(target_text_box.get_text()))))), self.colour_dict["Text"])
							self.username = target_text_box.get_text()
					case "password":
						
						# if within the character limit
						if len(target_text_box.get_text()) < 16:
							# update and display its text
							if key == "space":
								key = ""
							target_text_box.add_char(key)
							target_text_box.update()
							target_text_box.display_given_text("*" * len(target_text_box.get_text()), pygame.font.Font(resource_path("MainPrograms/Fonts/mine-sweeper.ttf"), int(POINT_SIZE * min(6.0, 7 - math.log2(1.5 * len(target_text_box.get_text()))))), self.colour_dict["Text"])
							self.password = target_text_box.get_text()
			else:
				match target_text_box.get_name().lower():
					case "username":
						# if within the character limit
						if len(target_text_box.get_text()) < 24:
							
							# update and display its text
							if key == "space":
								key = " "
							target_text_box.add_char(key)
							target_text_box.update()
							target_text_box.display_text(pygame.font.Font(resource_path("MainPrograms/Fonts/Roboto/static/Roboto-Bold.ttf"), int(POINT_SIZE * min(6.0, 7 - math.log2(max(1.0, 0.75 * len(target_text_box.get_text())))))), self.colour_dict["Text"])
							self.username = target_text_box.get_text()
					
					case "password":
						# if within the character limit
						if len(target_text_box.get_text()) < 16:
							
							# update and display its text
							if key == "space":
								key = ""
							target_text_box.add_char(key)
							target_text_box.update()
							target_text_box.display_text(pygame.font.Font(resource_path("MainPrograms/Fonts/Roboto/static/Roboto-Bold.ttf"), int(POINT_SIZE * min(6.0, 7 - math.log2(max(1.0, 0.75 * len(target_text_box.get_text())))))), self.colour_dict["Text"])
							self.password = target_text_box.get_text()
					
					case "confirm_password":
						# if within the character limit
						if len(target_text_box.get_text()) < 16:
							
							# update and display its text
							if key == "space":
								key = ""
							target_text_box.add_char(key)
							target_text_box.update()
							target_text_box.display_text(pygame.font.Font(resource_path("MainPrograms/Fonts/Roboto/static/Roboto-Bold.ttf"), int(POINT_SIZE * min(6.0, 7 - math.log2(max(1.0, 0.75 * len(target_text_box.get_text())))))), self.colour_dict["Text"])
							self.password_confirmed = target_text_box.get_text()
	
	def login_backspace(self) -> None:
		"""
			Events that happen when the screen type is generator_select and the user presses backspace

			Inputs:
				None
			Outputs:
				None

		"""
		
		# sets the type of the text box and target text box for ease of use
		text_box: TextInputBox
		target_text_box: TextInputBox | None = None
		
		# for each text box name
		for text_box_name in self._object_controller.text_box_dict.keys():
			
			# get the text box
			text_box = self._object_controller.text_box_dict[text_box_name]
			
			# if the text box is focused, save the text box and break
			if text_box.get_focused():
				target_text_box = text_box
				break
		
		# if a text box is focused
		if target_text_box is not None:
			
			# if there are character to delete
			if len(target_text_box.get_text()) > 0:
				# update and display its text
				
				if self.screen == "login":
					match target_text_box.get_name().lower():
						case "username":
							# update and display its text
							target_text_box.remove_char()
							target_text_box.update()
							target_text_box.display_text(pygame.font.Font(resource_path("MainPrograms/Fonts/Roboto/static/Roboto-Bold.ttf"), int(POINT_SIZE * min(6.0, 7 - math.log2(max(1.0, 0.75 * len(target_text_box.get_text())))))), self.colour_dict["Text"])
							self.username = target_text_box.get_text()
						case "password":
							# update and display its text
							target_text_box.remove_char()
							target_text_box.update()
							target_text_box.display_given_text("*" * len(target_text_box.get_text()), pygame.font.Font(resource_path("MainPrograms/Fonts/mine-sweeper.ttf"), int(POINT_SIZE * min(6.0, 7 - math.log2(max(1.0, 1.5 * len(target_text_box.get_text())))))), self.colour_dict["Text"])
							self.password = target_text_box.get_text()
				else:
					target_text_box.remove_char()
					target_text_box.update()
					target_text_box.display_text(pygame.font.Font(resource_path("MainPrograms/Fonts/Roboto/static/Roboto-Bold.ttf"), int(POINT_SIZE * min(6.0, 7 - math.log2(max(1.0, 0.75 * len(target_text_box.get_text())))))), self.colour_dict["Text"])
					
					match target_text_box.get_name().lower():
						case "username":
							# update and display its text
							self.username = target_text_box.get_text()
						case "password":
							# update and display its text
							self.password = target_text_box.get_text()
						case "confirm_password":
							# update and display its text
							self.password_confirmed = target_text_box.get_text()
	
	def validate_user(self):
		self.valid_login = self.validator.validate_login(self.username, self.password)
		if self.valid_login:
			self._object_controller.move_to_home_screen()
	
	def create_account(self) -> None:
		self.valid_login = self.validator.create_account(self.username,
														 self.password,
														 self.password_confirmed,
														 self.music_volume,
														 self.sfx_volume,
														 self.chording,
														 self.theme,
														 self.keybind_dict["dig"],
														 self.keybind_dict["flag"])
		if self.valid_login:
			self._object_controller.move_to_home_screen()
	
	def options_left_click(self, mouse_pos: Coordinate) -> None:
		"""
			Resolves a left click on the options screens
			
			Inputs:
				- mouse_pos: the position the mouse clicked
			Outputs:
				- None
		"""
		
		if self._ready:
			#if one of the keybind objects is focused, this input rebinds that event to left click
			if any(self._object_controller.keybind_dict[keybind_key].get_focused() for keybind_key in self._object_controller.keybind_dict.keys()):
				self.rebind_keybind(-1)
				return
			
			for toggle_box_key in self._object_controller.toggle_box_dict.keys():
				# if it is looking at a box that is not on the current menu, skip it
				if toggle_box_key[1] != self.screen:
					continue
				
				# get the box
				toggle_box = self._object_controller.toggle_box_dict[toggle_box_key]
				
				# check if it has been clicked
				check_clicked: bool = toggle_box.check_toggle_box_clicked(mouse_pos)
				
				#if the box was clicked
				if check_clicked:
					toggle_box.on_click()
					
					#if the user was logged in, update their settings
					if self.validator.get_user_logged_in():
						self.validator.set_option(toggle_box.get_active(), toggle_box.get_name())
			
			# sets the type of the keybind box for ease of use
			keybind_box: KeybindBox
			
			# for each keybind box name
			for keybind_key in self._object_controller.keybind_dict.keys():
				
				#if it is looking at a key that is not on the current menu, skip it
				if keybind_key[1] != self.screen:
					continue
				
				# get the keybind box
				keybind_box = self._object_controller.keybind_dict[keybind_key]
				
				# check if it has been clicked
				check_clicked: bool = keybind_box.check_keybind_box_clicked(mouse_pos)
				
				# set its focused state to whether it has been clicked
				keybind_box.set_focused(check_clicked)
				
				if keybind_box.get_focused():
					self._object_controller.box_dict[("key_change", "options")] = self.create_object(BoundingBox,
																									 (60 * self.POINT_SIZE, 10 * self.POINT_SIZE),
																									 self.WIN, (80 * self.POINT_SIZE), (10 * self.POINT_SIZE), self.POINT_SIZE, self.colour_dict["Background"], 4, self.colour_dict["Background"])
					self._object_controller.box_dict[("key_change", "options")].set_text(f"Press any key to rebind to {keybind_box.get_name().replace("_", " ").capitalize()}. Press Esc to cancel", font.Font(resource_path("MainPrograms/Fonts/Roboto/static/Roboto-Bold.ttf"), int(self.POINT_SIZE * 3)), colour=self.colour_dict["Border"])
			
			self._object_controller.options_left_click(mouse_pos)
		self._ready = True
	
	def rebind_keybind(self, new_keybind: int) -> None:
		"""
			Rebinds a keybind

			Inputs:
				- new_keybind: the integer value of the key pressed (note -1 is left click, -2 is right click)
			Outputs:
				- None
		"""
		# sets the type of the keybind box for ease of use
		keybind_box: KeybindBox
		
		# for each keybind box name
		for keybind_key in self._object_controller.keybind_dict.keys():
			
			# if it is looking at a key that is not on the current menu, skip it
			if keybind_key[1] != self.screen:
				continue
			
			# get the keybind box
			keybind_box = self._object_controller.keybind_dict[keybind_key]
			
			#if the keybind box
			if keybind_box.get_focused():
				
				#if the key pressed is the escape key, unfocus the keybind box and leave the function
				if new_keybind == 27:
					keybind_box.set_focused(False)
					self._object_controller.box_dict[("key_change", "options")].update()
					break
				
				#set the new key value
				keybind_box.set_key(new_keybind)
				
				if self.validator.get_user_logged_in():
					#update it in the database
					self.validator.set_keybind(keybind_box.get_name(), new_keybind)
				self.keybind_dict[keybind_box.get_name()] = new_keybind
				
				#draw the new keybind box
				keybind_box.update()
				keybind_box.display_text(keybind_box.get_text(), pygame.font.Font(resource_path("MainPrograms/Fonts/Roboto/static/Roboto-Bold.ttf"), int(self.POINT_SIZE * min(6.0, 7 - math.log2(max(1.0, 0.75 * len(keybind_box.get_text())))))), self.colour_dict["Text"])
				
				#unfocus the box
				keybind_box.set_focused(False)
				
				self._object_controller.box_dict[("key_change", "options")].update()
				break
	
	def zoom(self, mouse_x: float, mouse_y: float, zoom_multiplier: float) -> None:
		"""
			Zooms the tile board in or out, centred upon the mouse position
			
			Inputs:
				- mouse_x: the mouse's x-position
				- mouse_y: the mouse's y-position
				- zoom_multiplier: the multiplier which dictates how much the screen zooms in or out
		
		"""
		# save the previous zoom state
		previous_zoom = self.tile_surface_zoom
		
		# update the zoom level depending on whether we zoomed in or out - cap between 0.2x and 2x
		self.tile_surface_zoom *= zoom_multiplier
		self.tile_surface_zoom = max(0.2, min(self.tile_surface_zoom, 2))
		
		# skip if no change
		if previous_zoom == self.tile_surface_zoom:
			return
		
		# clear the board
		WIN.fill(self.colour_dict["Background"])
		
		# save the position of the mouse so that we can make sure it stays constant
		old_tile_surface_position = ((mouse_x + self.tile_surface_offset[0]) / previous_zoom, (mouse_y + self.tile_surface_offset[1]) / previous_zoom)
		
		# set the new position of the top left corner of the tile surface
		self.tile_surface_offset = (old_tile_surface_position[0] * self.tile_surface_zoom - mouse_x, old_tile_surface_position[1] * self.tile_surface_zoom - mouse_y)
		
		# save the dimensions of the surface
		temp_dimensions = self.tile_surface_dims[0] * self.tile_surface_zoom, self.tile_surface_dims[1] * self.tile_surface_zoom
		
		# save the zoomed surface
		self.zoomed_tile_surface = pygame.transform.smoothscale(self.tile_surface, temp_dimensions)
		
		# display the surface
		WIN.blit(self.zoomed_tile_surface, (-self.tile_surface_offset[0], -self.tile_surface_offset[1]))
		self._object_controller.redraw_gameplay_screen()
	
	def main(self) -> None:
		"""
			This is the main entrance point of the whole program. Everything that it executed in the final version of
			the project is executed through here.

			This procedure contains the main event loop, where the same set of events are executed every game tick (which
			is every frame).
		"""
		#initialize global clock
		clock = pygame.time.Clock()
		
		#move to the gameplay screen
		self.workers, self.task_queue, self.result_queue = self._object_controller.move_to_first_loading_screen()
		
		#have a maximum of 16 sound effects being able to be played at once
		pygame.mixer.set_num_channels(16)
		
		#load and play the background music
		pygame.mixer.music.load(resource_path("MainPrograms/Sounds/MINE - faded.wav"))
		pygame.mixer.music.set_volume(self.music_volume)
		pygame.mixer.music.play(loops=-1)
		
		# main event loop
		while self._run:
			#wait so it runs in at a set frame rate
			clock.tick(self.FPS)
			
			# check for events
			for event in pygame.event.get():
				
				# if "x" button clicked, close the game
				if event.type == pygame.QUIT:
					#close all external processes
					self.task_queue.close()
					for worker in self.workers:
						worker.terminate()
						worker.join()
					
					#close the database connection
					self.validator.close_connection()
					self._run = False
					pygame.quit()
					sys.exit()
				
				# if the mouse button is clicked, get the positions of the mouse
				elif event.type == pygame.MOUSEBUTTONDOWN:
					
					#if left click
					if pygame.mouse.get_pressed()[0]:
						
						#get mouse position, and check if any buttons were clicked
						click_mouse_x, click_mouse_y = pygame.mouse.get_pos()
						self._object_controller.check_button_clicked((click_mouse_x, click_mouse_y), self.screen)
						
						#only while on the gameplay screen
						if self.screen == "gameplay":
							
							#if within the board dimensions
							if 60 * self.POINT_SIZE < click_mouse_x < 140 * self.POINT_SIZE and 25 * self.POINT_SIZE < click_mouse_y < 105 * self.POINT_SIZE:
								
								#if flag is right click
								if self.keybind_dict["flag"] == -1:
									self.gameplay_right_click((click_mouse_x, click_mouse_y))
								
								#if dig is right click
								elif self.keybind_dict["dig"] == -1:
									self.gameplay_left_click((click_mouse_x, click_mouse_y))
							else:
								#prevent automatically clicking upon entering a new screen
								self._ready = True
						elif self.screen == "generator_select":
							self._object_controller.generator_select_left_click((click_mouse_x, click_mouse_y))
						elif self.screen == "offset":
							self.offset_left_click((click_mouse_x, click_mouse_y))
						elif self.screen == "options":
							self.options_left_click((click_mouse_x, click_mouse_y))
						elif self.screen == "tutorial":
							if self.keybind_dict["flag"] == -1:
								self.tutorial_right_click((click_mouse_x, click_mouse_y))
							elif self.keybind_dict["dig"] == -1:
								self.tutorial_left_click((click_mouse_x, click_mouse_y))
						
						else:
							self._object_controller.left_click((click_mouse_x, click_mouse_y))
					
					#if right click
					if pygame.mouse.get_pressed()[2]:
						
						#get mouse position, and check if any buttons were clicked
						click_mouse_x, click_mouse_y = pygame.mouse.get_pos()
						
						#only on the gameplay screen
						if self.screen == "gameplay":
							if 60 * self.POINT_SIZE < click_mouse_x < 140 * self.POINT_SIZE and 25 * self.POINT_SIZE < click_mouse_y < 105 * self.POINT_SIZE:
								if self.keybind_dict["flag"] == -2:
									self.gameplay_right_click((click_mouse_x, click_mouse_y))
								elif self.keybind_dict["dig"] == -2:
									self.gameplay_left_click((click_mouse_x, click_mouse_y))
						elif self.screen == "options":
							self.rebind_keybind(-2)
						elif self.screen == "tutorial":
							if self.keybind_dict["flag"] == -2:
								self.tutorial_right_click((click_mouse_x, click_mouse_y))
							elif self.keybind_dict["dig"] == -2:
								self.tutorial_left_click((click_mouse_x, click_mouse_y))
				
				#if a key is pressed
				elif event.type == pygame.KEYDOWN:
					
					#if the current screen is generator_select
					if self.screen == "generator_select":
						
						#if the key is backspace, call the backspace function
						if event.key == pygame.K_BACKSPACE:
							self.generator_select_backspace()
						
						#if the key is a character, call the keydown function
						elif pygame.key.name(event.key) in string.ascii_letters + string.digits:
							self.generator_select_keydown(pygame.key.name(event.key))
						
						#if the key is a shift key, set the shift state to true
						elif event.key == pygame.K_LSHIFT or event.key == pygame.K_RSHIFT:
							self._shift_active = True
					
					elif self.screen == "login" or self.screen == "create_account":
						# if the key is a shift key, set the shift state to true
						if event.key == pygame.K_LSHIFT or event.key == pygame.K_RSHIFT:
							self._shift_active = True
						elif event.key == pygame.K_BACKSPACE:
							self.login_backspace()
						elif pygame.key.name(event.key) in string.ascii_letters + string.digits + string.punctuation + "space":
							self.login_keydown(pygame.key.name(event.key))
					elif self.screen == "options":
						self.rebind_keybind(event.key)
					
					#if the current screen is the gameplay screen
					elif self.screen == "gameplay":
						
						#get the mouse position
						mouse_pos: Coordinate = pygame.mouse.get_pos()
						
						#if within the board area
						if 60 * self.POINT_SIZE < mouse_pos[0] < 140 * self.POINT_SIZE and 25 * self.POINT_SIZE < mouse_pos[1] < 105 * self.POINT_SIZE:
							
							#prevent need for double click
							self._ready = True
							
							#if the flag keybind was clicked, resolve right click
							if event.key == self.keybind_dict["flag"]:
								self.gameplay_right_click(mouse_pos)
							# if the dig keybind was clicked, resolve left click
							elif event.key == self.keybind_dict["dig"]:
								self.gameplay_left_click(mouse_pos)
				
				#if a key is no longer being pressed
				elif event.type == pygame.KEYUP:
					
					#if the shift key is no longer being pressed, set the shift state to false
					if not (pygame.key.get_pressed()[pygame.K_LSHIFT] or pygame.key.get_pressed()[pygame.K_RSHIFT]):
						self._shift_active = False
				
				# if the wheel is scrolled
				elif event.type == pygame.MOUSEWHEEL:
					
					#get the position of the mouse
					mouse_x, mouse_y = pygame.mouse.get_pos()
					
					#if the current screen is gameplay
					if self.screen == "gameplay":
						
						#if within the board dimensions and the initial zoom animation is not active
						if 60 * self.POINT_SIZE < mouse_x < 140 * self.POINT_SIZE and 25 * self.POINT_SIZE < mouse_y < 105 * self.POINT_SIZE and self.zoom_animation_count == 0:
							self.zoom(mouse_x, mouse_y, 1.1 ** event.y)
			
			#only for gameplay screen
			if self.screen == "gameplay":
				
				# update the timer
				if self.gameplay_active:
					self._object_controller.box_dict[("time_box", "gameplay")].update()
					self._object_controller.box_dict[("time_box", "gameplay")].set_text(f"{time.perf_counter() - self.start_time: 0.2f}", TIME_FONT, self.colour_dict["Text"])
					
					#if there are still frames of the zoom animation, zoom in a bit
					if self.zoom_animation_count > 0:
						self.zoom(self.zoom_animation_centre[0], self.zoom_animation_centre[1], zoom_multiplier=self.zoom_animation_multiplier)
						
						#decrement the remaining frame count
						self.zoom_animation_count -= 1
				
				#get the position of the mouse
				mouse_x, mouse_y = pygame.mouse.get_pos()
				
				#if within the board dimensions and the initial zoom animation is not active
				if 60 * self.POINT_SIZE < mouse_x < 140 * self.POINT_SIZE and 25 * self.POINT_SIZE < mouse_y < 105 * self.POINT_SIZE and self.zoom_animation_count == 0:
					#if the middle mouse button is pressed
					if pygame.mouse.get_pressed()[1]:
						#clear the window
						WIN.fill(self.colour_dict["Background"])
						
						#get the mouse movement since the last call
						mouse_movement_x, mouse_movement_y = pygame.mouse.get_rel()
						
						#update the offset based off this
						self.tile_surface_offset = self.tile_surface_offset[0] - mouse_movement_x, self.tile_surface_offset[1] - mouse_movement_y
						
						#avoid value not found error
						if self.zoomed_tile_surface is None:
							self.zoomed_tile_surface = self.tile_surface
						
						#display the new surface
						WIN.blit(self.zoomed_tile_surface, (-self.tile_surface_offset[0], -self.tile_surface_offset[1]))
						self._object_controller.redraw_gameplay_screen()
					else:
						pygame.mouse.get_rel()
			
			elif self.screen == "options":
				# get the position of the mouse
				mouse_pos = pygame.mouse.get_pos()
				self._object_controller.move_sliders(mouse_pos, "options")
			
			#reset the volume
			mixer_volume = pygame.mixer.music.get_volume()
			if mixer_volume != self.music_volume or self.quieten_active:
				if not any(pygame.mixer.Channel(i).get_busy() for i in range(16)):
					#fade back to default
					if self.music_volume - mixer_volume > 0:
						pygame.mixer.music.set_volume(mixer_volume + max(abs(self.music_volume - mixer_volume) / 40, 0.003))
				
				elif self.quieten_active and mixer_volume > 3 * self.music_volume / 5:
					pygame.mixer.music.set_volume(mixer_volume - max(abs((3 * self.music_volume / 5) - mixer_volume) / 20, 0.005))
				
				mixer_volume = pygame.mixer.music.get_volume()
				if abs(self.music_volume - mixer_volume) <= 0.003:
					pygame.mixer.music.set_volume(self.music_volume)
					self.quieten_active = False
			
			#update the screen
			pygame.display.update()
		
		# close the game
		self.task_queue.close()
		for worker in self.workers:
			worker.terminate()
			worker.join()
		
		# close the database connection
		self.validator.close_connection()
		self._run = False
		pygame.quit()
		sys.exit()


def resource_path(relative_path):
	if hasattr(sys, "_MEIPASS"):
		return os.path.join(sys._MEIPASS, relative_path)
	return os.path.join(os.path.abspath("."), relative_path)


if __name__ == "__main__":
	# starts pygame
	pygame.mixer.pre_init(
		frequency=44100,
		size=-16,
		channels=2,
		buffer=128
	)
	pygame.init()
	pygame.display.set_caption("Minecells")
	
	#starts multiprocessing
	mp.freeze_support()
	
	# defines a surface, which is our main screen, and sets it to be fullscreen
	WIN: Surface = pygame.display.set_mode((1920, 1080))
	
	POINT_SIZE: float = WIN.get_width() / 200
	
	# Fonts
	TEXTBOX_FONT = pygame.font.Font(resource_path("MainPrograms/Fonts/Roboto/static/Roboto-Bold.ttf"), int(POINT_SIZE * 6))
	TEXTBOX_FONT_2 = pygame.font.Font(resource_path("MainPrograms/Fonts/Roboto/static/Roboto-Bold.ttf"), int(POINT_SIZE * 3))
	TIME_FONT = pygame.font.Font(resource_path("MainPrograms/Fonts/Roboto/static/Roboto-Bold.ttf"), int(POINT_SIZE * 3))
	FONT = pygame.font.Font(resource_path("MainPrograms/Fonts/Roboto/static/Roboto-Bold.ttf"), int(POINT_SIZE * 4))
	TILE_FONT = pygame.font.Font(resource_path("MainPrograms/Fonts/mine-sweeper.ttf"), int(POINT_SIZE * 4))
	
	# Set a frame rate to time the event loop
	FPS: int = 60
	
	main_class = MainProgram(WIN, FONT, TILE_FONT, FPS)
	
	main_class.main()
