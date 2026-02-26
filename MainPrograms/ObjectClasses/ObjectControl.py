import pygame
import multiprocessing as mp
import math
import random
import time
import sys
import os

from MainPrograms.ObjectClasses.BoundingBox import BoundingBox
from MainPrograms.ObjectClasses.DropdownBox import DropdownBox, DropdownOption
from MainPrograms.ObjectClasses.KeybindBox import KeybindBox
from MainPrograms.ObjectClasses.Slider import Slider, SliderOrb
from MainPrograms.ObjectClasses.Tile import Tile
from MainPrograms.ObjectClasses.Button import Button
from MainPrograms.ObjectClasses.TextInputBox import TextInputBox
from MainPrograms.ObjectClasses.ToggleBox import ToggleBox
from typing import Type, TypeVar
from pygame import Surface, font

type Coordinate = tuple[float, float]
type Colour = tuple[int, int, int]
type TilePosition = tuple[int, int]
type Board = list[list[int]]
ClassVariable = TypeVar("ClassVariable")


# noinspection PyProtectedMember
def resource_path(relative_path):
	"""
		Converts a relative path to a file into an absolute path

		Inputs:
			- relative_path: the relative path from the root directory of the target file
		Outputs:
			- the absolute path to the target file
	"""
	
	# if running as a bundled process (ie as an exe)
	if hasattr(sys, "_MEIPASS"):
		return os.path.join(sys._MEIPASS, relative_path)
	
	# if running as a normal .py file
	return os.path.join(os.path.abspath("."), relative_path)


class ObjectControl:
	def __init__(self, main, surface: Surface, text_font: font.Font, tile_font: font.Font, textbox_font: font.Font, textbox_font_2: font.Font, time_font: font.Font, fps: int = 60):
		"""
			Constructor class for the ObjectControl class

			Inputs:
				- surface: the WIN surface
				- *fonts: a series of fonts for different scenarios
				- fps: the frame rate to be used by the system (60 by default)
			Initializes:
				- self._WIN: the WIN surface
				- self.WIDTH: the width of the WIN surface
				- self.HEIGHT: the height of the WIN surface
				- self.POINT_SIZE: the point unit to ensure that the screen scales to any screen dimensions
				- self.FONT: the font to be used by the text informing the user
				- self.TILE_FONT: the font to be used by the tiles
				- self.FPS: the frame rate to be used by the system (60 by default)
				- self._main: the variable self of the MainProgram class
				- Other class variables initialized in other parts in the class, which have to be initialized here

		"""
		# Initialise main attribute variables
		self.WIN: Surface = surface
		self.WIDTH: int = surface.get_width()
		self.HEIGHT: int = surface.get_height()
		self.POINT_SIZE: float = self.WIDTH / 200
		self.FONT: font.Font = text_font
		self.TILE_FONT: font.Font = tile_font
		self.TEXTBOX_FONT: font.Font = textbox_font
		self.TEXTBOX_FONT_2: font.Font = textbox_font_2
		self.TIME_FONT = time_font
		self.FPS: int = fps
		self._main = main
		
		self.button_dict: dict[tuple[str, str]:Button] = {}  #dictionary of all button objects alongside their on click functions
		self.text_box_dict: dict[tuple[str, str]:TextInputBox] = {}  #dictionary of all text boxes
		self.box_dict: dict[tuple[str, str]:BoundingBox] = {}  #dictionary of all bounding boxes
		self.toggle_box_dict: dict[tuple[str, str]:ToggleBox] = {}  #dictionary of all toggle boxes
		self.dropdown_dict: dict[tuple[str, str]:tuple[DropdownBox, *DropdownOption]] = {}  #dictionary of all dropdown menus alongside their dropdown options
		self.keybind_dict: dict[tuple[str, str]:KeybindBox] = {}  #dictionary of all keybind boxes
		self.slider_dict: dict[tuple[str, str]:tuple[Slider, SliderOrb]] = {}  #dictionary of all sliders alongside their orbs
		self.tutorial_board_dict: dict[tuple[int, int]:tuple[list[list[Tile]]], Board, Board] = {}  #dictionary of all tutorial private, public and tile boards
		self.tile_board: list[list[Tile]] = []  #the current tile board
		self.offset_tile_board: list[list[Tile]] = []  #the tile board indicating offset directions
	
	@staticmethod
	def create_object(object_class: Type[ClassVariable], position: Coordinate, *args, draw: bool = True) -> ClassVariable:
		"""
			Function to create and display a new object
		
			Inputs:
				- object_class: the class to create the instance from
				- position: the position of the object
				- arguments of the object
				- draw: whether to draw the object (default True)
			Outputs:
				- object_created: the object that was created as a result of this function
		"""
		
		#create the object
		object_created: object = object_class(*args)
		
		#positon the object
		object_created.set_pos(position)
		
		#draw the object if draw is true
		if draw:
			object_created.draw()
		
		#return the object created
		return object_created
	
	def check_button_clicked(self, mouse_pos: Coordinate, screen: str) -> None:
		"""
			Checks if a button on the screen was clicked, and resolves its on click effect if so.
			
			Inputs:
				- mouse_pos: the position of the mouse on the screen
				- screen: the current screen the user is on
			Outputs:
				- None
		"""
		
		for button_name in self.button_dict.keys():
			
			#skip if not on the screen
			if button_name[1] != screen:
				continue
			
			#get the target button
			target_button: Button = self.button_dict[button_name][0]
			
			#if the button was clicked and is active
			if target_button.check_button_click(mouse_pos) and target_button.get_active():
				self.button_dict[button_name][1]()
				
				#if the button is the start button, or the exit button, don't play a sound
				if "start" in button_name[0] or "exit" in button_name[0]:
					break
				
				#else play a random sound (between 3 and 5)
				self._main.quieten_active = True
				num = random.randint(3, 5)
				press_sound = pygame.mixer.Sound(resource_path(f"MainPrograms/Sounds/MINESWEEPER SFX - {num} - faded.wav"))
				
				#reduce volume, as the sound is quite loud
				pygame.mixer.Sound.set_volume(press_sound, self._main.sfx_volume)
				press_sound.play()
				break
	
	@staticmethod
	def check_tile_clicked(tile_board: list[list[Tile]], mouse_pos: Coordinate, zoom: float, offset: tuple[float, float]) -> TilePosition | None:
		"""
			Check if a gameplay tile was clicked
			
			Inputs:
				- tile_board: the list of all tile objects arranged as a grid
				- mouse_pos: the position of the mouse on the screen
				- zoom: the current board zoom level
				- offset: the current board offset level
			Outputs:
				- TilePosition: the position of the tile clicked (None if no tile clicked)
		"""
		for row in tile_board:
			for tile in row:
				if tile.check_tile_clicked(mouse_pos, zoom, offset):
					return tile.on_click()
		return None
	
	def unfocus_boxes(self) -> None:
		"""
			Clear the focused condition from all text boxes
			
			Inputs:
				- None
			Outputs:
				- None
		"""
		for text_box_name in self.text_box_dict.keys():
			text_box = self.text_box_dict[text_box_name]
			
			text_box.set_focused(False)
	
	def reset_active(self) -> None:
		"""
			Sets all text boxes and buttons that are inactive by default to be inactive
			
			Inputs:
				- None
			Outputs:
				- None
		"""
		
		#for each text box
		for text_box_name in self.text_box_dict.keys():
			
			#get the text box object
			text_box = self.text_box_dict[text_box_name]
			
			#set it to inactive
			if text_box.get_name() in ["difficulty", "spaces"]:
				text_box.set_active(False)
		
		# for each button
		for button_name in self.button_dict.keys():
			# get the button
			button = self.button_dict[button_name][0]
			
			# set it to inactive
			if button.get_name() == "offset":
				button.set_active(False)
	
	def close_game(self) -> None:
		"""
			Function to be passed as a parameter for the on_click for the exit button
			so that it can modify the run variable directly

			Inputs:
				- None
			Outputs:
				- None
		"""
		self._main.close_safely()
	
	def init_game(self) -> None:
		"""
			Sets the game up so that the user can click the first tile

			Inputs:
				- None
			Outputs:
				- None
		"""
		
		# sets the mode such that the main loop knows that it is in this state
		
		# reset the board
		for row in self.tile_board:
			for tile in row:
				tile.update()
		
		# hides any present text
		text_cover = self.create_object(BoundingBox,
										(70 * self.POINT_SIZE, 15 * self.POINT_SIZE),
										self.WIN, (60 * self.POINT_SIZE), (10 * self.POINT_SIZE), self.POINT_SIZE, self._main.colour_dict["Background"], 0, self._main.colour_dict["Background"])
		text_cover.update()
		
		# tells the user to select a starting tile
		text = self.create_object(BoundingBox,
								  (100 * self.POINT_SIZE, 20 * self.POINT_SIZE),
								  self.WIN, 0, 0, self.POINT_SIZE, self._main.colour_dict["Background"], 0, self._main.colour_dict["Background"])
		text.set_text("Please select starting tile", self.FONT, self._main.colour_dict["Text"])
		
		self.box_dict[("board_box", "gameplay")].draw()
	
	def start_game(self, minecount: int, screen: str = "gameplay") -> None:
		"""
			Starts the game after the first click

			Inputs:
				- start_position: the position the user clicked
			Outputs:
				- None
		"""
		# updates the minecount
		self.box_dict[("minecount_box", screen)].update()
		self.box_dict[("minecount_box", screen)].set_text(str(minecount), self.FONT, self._main.colour_dict["Text"])
		
		# redraws the board box
		self.box_dict[("board_box", screen)].draw()
		
		# resets the timer
		self.box_dict[("time_box", screen)].set_text("0.00", self.TIME_FONT, self._main.colour_dict["Text"])
	
	def generator_select_left_click(self, mouse_pos: Coordinate) -> None:
		"""
			Events that happen when the screen type is generator_select and the user does a left click

			Inputs:
				- mouse_pos: the position of the mouse
			Outputs:
				None

		"""
		
		# sets the type of the text box for ease of use
		text_box: TextInputBox
		
		# for each text box name
		for text_box_key in self.text_box_dict.keys():
			
			# get the text box
			text_box = self.text_box_dict[text_box_key]
			
			#skip if text box is not active
			if not text_box.get_active():
				continue
			
			# check if it has been clicked
			check_clicked: bool = text_box.check_text_box_clicked(mouse_pos)
			
			# if the user has clicked off of a focused text box while it has no text in it, reset it to seed
			if len(text_box.get_text()) == 0 and text_box.get_focused() and not check_clicked:
				text_box.update()
				text_box.set_text(text_box.get_name().capitalize(), self.TEXTBOX_FONT, self._main.colour_dict["Text"])
			
			# set its focused state to whether it has been clicked
			text_box.set_focused(check_clicked)
		
		#for each dropdown button
		for dropdown_key in self.dropdown_dict.keys():
			if dropdown_key[1] != "generator_select":
				continue
			
			dropdown_box: DropdownBox
			
			#get the button and its options
			dropdown_box, *dropdown_options = self.dropdown_dict[dropdown_key]
			
			#check if the dropdown box was clicked
			check_clicked = dropdown_box.check_drop_box_clicked(mouse_pos)
			
			#if it was clicked and is not already focused
			if check_clicked and not dropdown_box.get_focused():
				
				#it is now focused
				dropdown_box.set_focused(True)
				
				#for each of its options
				for i in range(len(dropdown_options)):
					#get its option
					dropdown_option: DropdownOption = dropdown_options[i]
					
					#display it
					dropdown_option.set_pos((30 * self.POINT_SIZE, 31 * self.POINT_SIZE + (11 * self.POINT_SIZE * i)))
					dropdown_option.set_visible(True)
					dropdown_option.update()
					
					#display the text
					dropdown_option.set_text(dropdown_option.get_name(), self.TEXTBOX_FONT_2, self._main.colour_dict["Text"])
			
			#if it is clicked and is already focused
			elif check_clicked and dropdown_box.get_focused():
				
				#it is now not focused
				dropdown_box.set_focused(False)
				
				#set its gamemode to the default
				dropdown_box.set_current_option("Standard")
				
				# set its gamemode to the default "Standard"
				self._main.generator = "Standard"
				
				#redraw the screen
				self.move_to_generator_select()
			
			#for each dropdown option
			for i in range(len(dropdown_options)):
				dropdown_option: DropdownOption = dropdown_options[i]
				
				#if it is not visible, none of them are so skip
				if not dropdown_option.get_visible():
					break
				
				#check if it clicked
				dropdown_clicked = dropdown_option.check_drop_option_clicked(mouse_pos)
				
				#if it has been clicked
				if dropdown_clicked:
					#redraw the screen
					dropdown_box.update()
					dropdown_box.set_current_option(dropdown_option.get_name().capitalize())
					
					#set the generator
					self._main.generator = dropdown_option.get_name()
					
					# redraw the screen
					self.move_to_generator_select()
					
					#it is now no longer focused
					dropdown_box.set_focused(False)
	
	def left_click(self, mouse_pos: Coordinate) -> None:
		"""
			Events that happen when the screen type is login and the user does a left click

			Inputs:
				- mouse_pos: the position of the mouse
			Outputs:
				None

		"""
		
		# sets the type of the text box for ease of use
		text_box: TextInputBox
		
		# for each text box name
		for text_box_key in self.text_box_dict.keys():
			
			if text_box_key[1] != self._main.screen:
				continue
			
			# get the text box
			text_box = self.text_box_dict[text_box_key]
			
			# check if it has been clicked
			check_clicked: bool = text_box.check_text_box_clicked(mouse_pos)
			
			# if the user has clicked off of a focused text box while it has no text in it, reset it to seed
			if len(text_box.get_text()) == 0 and text_box.get_focused() and not check_clicked:
				text_box.update()
				text_box.set_text(text_box.get_name().replace("_", " ").capitalize(), self.TEXTBOX_FONT, self._main.colour_dict["Text"])
			
			# set its focused state to whether it has been clicked
			text_box.set_focused(check_clicked)
	
	def move_to_gameplay_screen(self) -> None:
		"""
			Moves to the screen for the gameplay

			Inputs:
				- None
			Outputs:
				- None

		"""
		
		#if there is an error, prevent the user from entering the screen
		if self._main.validator.get_error():
			return
		
		#clear the active condition from the text boxes
		self.reset_active()
		
		#clear the focused condition from all text boxes
		self.unfocus_boxes()
		
		# sets the background to white at the start of the program
		self.WIN.fill(self._main.colour_dict["Background"])
		
		#generate the dimensions of the tile surface based on the board size
		self._main.tile_surface_dims = (10 * self._main.board_cols * self.POINT_SIZE, 10 * self._main.board_rows * self.POINT_SIZE)
		
		# draw all the tiles
		self.tile_board = []
		
		#create the tile surface
		self._main.tile_surface = pygame.Surface((10 * self._main.board_cols * self.POINT_SIZE, 10 * self._main.board_rows * self.POINT_SIZE))
		
		#set it to the background colour
		self._main.tile_surface.fill(self._main.colour_dict["Background"])
		
		#clear the zoomed tile surface to indicate the surface hasn't been zoomed in or out yet
		self._main.zoomed_tile_surface = None
		
		#set zoom and offset to default values
		self._main.tile_surface_zoom = 1
		self._main.tile_surface_offset = (5 * self._main.board_cols * self.POINT_SIZE - 100 * self.POINT_SIZE, 5 * self._main.board_rows * self.POINT_SIZE - 65 * self.POINT_SIZE)
		
		#create the tile board
		#for each row
		for rows in range(self._main.board_rows):
			#initialize a list to contain the tiles for that row
			row: list[Tile] = []
			
			#for each column
			for cols in range(self._main.board_cols):
				#initialize, set the position and draw the tile
				tile = Tile(
					surface=self._main.tile_surface,
					tile_size=10 * self.POINT_SIZE,
					point_size=self.POINT_SIZE,
					border_colour=self._main.colour_dict["Border"],
					border_width=1,
					tile_coordinate=(rows, cols),
					rows=self._main.board_rows,
					cols=self._main.board_cols,
					text_colour_start=self._main.colour_dict["Tile start"],
					text_colour_end=self._main.colour_dict["Tile end"],
					background_colour=self._main.colour_dict["Background"])
				tile.set_pos((10 * self.POINT_SIZE * cols, 10 * self.POINT_SIZE * rows))
				tile.draw()
				
				#set its value to be empty
				tile.set_value(-2)
				
				#add it to the row
				row.append(tile)
			#add the row to the tile board
			self.tile_board.append(row)
		
		#display the board on the screen
		self.WIN.blit(self._main.tile_surface, (-self._main.tile_surface_offset[0], -self._main.tile_surface_offset[1]))
		
		#cover up the parts of the screen that are not the board to prevent the board from leaving the intended box
		#top
		cover = BoundingBox(self.WIN, 60 * self.POINT_SIZE, 200 * self.POINT_SIZE, self.POINT_SIZE, self._main.colour_dict["Background"], 0, self._main.colour_dict["Background"])
		cover.update()
		#bottom
		cover.set_pos((140 * self.POINT_SIZE, 0))
		cover.update()
		#left
		cover = BoundingBox(self.WIN, 200 * self.POINT_SIZE, 25 * self.POINT_SIZE, self.POINT_SIZE, self._main.colour_dict["Background"], 0, self._main.colour_dict["Background"])
		cover.set_pos((0, 0))
		cover.update()
		#right
		cover.set_pos((0, 105 * self.POINT_SIZE))
		cover.update()
		
		# defines and draws an exit button to be used to close the game
		self.button_dict[("exit_button", "gameplay")]: Button = (self.create_object(Button,
																					(self.WIDTH - (5 * self.POINT_SIZE) - self.POINT_SIZE, self.POINT_SIZE),
																					self.WIN, self.POINT_SIZE, (5 * self.POINT_SIZE), (5 * self.POINT_SIZE), self._main.colour_dict["No"], "exit_button", 0, self._main.colour_dict["Background"]),
																 self.close_game)
		
		# defines and draws a back button to be used to return to the previous screen
		self.button_dict[("back_button", "gameplay")]: Button = (self.create_object(Button,
																					(self.POINT_SIZE, self.POINT_SIZE),
																					self.WIN, self.POINT_SIZE, (5 * self.POINT_SIZE), (5 * self.POINT_SIZE), self._main.colour_dict["Back"], "back_button", 0, self._main.colour_dict["Background"]),
																 self.move_to_generator_select)
		self.button_dict[("back_button", "gameplay")][0].set_text("<-", self.FONT, self._main.colour_dict["Text"])
		
		# defines and draws a back button to be used to return to the previous screen
		self.button_dict[("reset_button", "gameplay")]: Button = (self.create_object(Button,
																					 (75 * self.POINT_SIZE, 5 * self.POINT_SIZE),
																					 self.WIN, self.POINT_SIZE, (10 * self.POINT_SIZE), (10 * self.POINT_SIZE), self._main.colour_dict["Border"], "reset_button", 4, (255, 255, 255)),
																  self.move_to_gameplay_screen)
		self.button_dict[("reset_button", "gameplay")][0].update()
		self.button_dict[("reset_button", "gameplay")][0].set_image(resource_path("MainPrograms/reset.png"))
		
		# defines and draws a bounding box that will contain the minecount
		self.box_dict[("minecount_box", "gameplay")]: BoundingBox = self.create_object(BoundingBox,
																					   (95 * self.POINT_SIZE, 5 * self.POINT_SIZE),
																					   self.WIN, (10 * self.POINT_SIZE), (10 * self.POINT_SIZE), self.POINT_SIZE, self._main.colour_dict["Border"], 4, self._main.colour_dict["Background"])
		self.box_dict[("minecount_box", "gameplay")].set_text("N/A", self.FONT, self._main.colour_dict["Text"])
		
		# defines and draws a bounding box that will contain the board
		self.box_dict[("board_box", "gameplay")]: BoundingBox = self.create_object(BoundingBox,
																				   (60 * self.POINT_SIZE, 25 * self.POINT_SIZE),
																				   self.WIN, (80 * self.POINT_SIZE), (80 * self.POINT_SIZE), self.POINT_SIZE, self._main.colour_dict["Border"], 5, self._main.colour_dict["Background"])
		
		# defines and draws a bounding box that will display the time spent on the board
		self.box_dict[("time_box", "gameplay")]: BoundingBox = self.create_object(BoundingBox,
																				  (115 * self.POINT_SIZE, 5 * self.POINT_SIZE),
																				  self.WIN, (10 * self.POINT_SIZE), (10 * self.POINT_SIZE), self.POINT_SIZE, self._main.colour_dict["Border"], 4, self._main.colour_dict["Background"])
		self.box_dict[("time_box", "gameplay")].set_text("0.00", self.TIME_FONT, self._main.colour_dict["Text"])
		
		#quiten the volume during gameplay
		self._main.music_volume = self._main.music_volume * 2 / 5
		self._main.quieten_active = True
		
		# calculate how much to zoom to fit the entire board on the screen
		zoom_factor: float = min(80 / (10 * self._main.board_cols), 80 / (10 * self._main.board_rows))
		
		# zoom in/ out
		self._main.zoom(100 * self.POINT_SIZE, 65 * self.POINT_SIZE, zoom_multiplier=zoom_factor)
		
		if "puzzle" not in self._main.generator.lower():
			# set screen type
			if self._main.screen == "gameplay":
				self._main.init_game(True)
			else:
				self._main.screen = "gameplay"
				
				# start a game immediately
				self._main.init_game(False)
		else:
			# set screen type
			self._main.screen = "gameplay"
			
			#set up variables to move to gameplay
			self._main._ready = False
			self._main.start_active = False
			self._main.gameplay_active = True
			self._main.start_time = time.perf_counter()
			self._main.start_game((0, 0))
	
	def redraw_gameplay_screen(self, screen: str = "gameplay") -> None:
		"""
			Redraw the gameplay screen after a zoom
			
			Inputs:
				- screen: the current screen to redraw
			Outputs:
				- None
		"""
		
		# cover up the parts of the screen that are not the board to prevent the board from leaving the intended box
		# top
		cover = BoundingBox(self.WIN, 60 * self.POINT_SIZE, 200 * self.POINT_SIZE, self.POINT_SIZE, self._main.colour_dict["Background"], 0, self._main.colour_dict["Background"])
		cover.update()
		# bottom
		cover.set_pos((140 * self.POINT_SIZE, 0))
		cover.update()
		# left
		cover = BoundingBox(self.WIN, 200 * self.POINT_SIZE, 25 * self.POINT_SIZE, self.POINT_SIZE, self._main.colour_dict["Background"], 0, self._main.colour_dict["Background"])
		cover.set_pos((0, 0))
		cover.update()
		# right
		cover.set_pos((0, 105 * self.POINT_SIZE))
		cover.update()
		
		#draw the time box
		self.box_dict[("time_box", screen)].draw()
		
		#if start active, then it is before the user has made the first click so set the time to 0
		if self._main.start_active:
			self.box_dict[("time_box", screen)].set_text("0.00", self.TIME_FONT, self._main.colour_dict["Text"])
		# if gameplay active, then it is during gameplay, so set time to current time
		elif self._main.gameplay_active:
			self.box_dict[("time_box", screen)].set_text(f"{time.perf_counter() - self._main.start_time: 0.2f}", self.TIME_FONT, self._main.colour_dict["Text"])
		#if the user has won or lost, set the time to their final time
		elif self._main.won or not self._main.alive:
			self.box_dict[("time_box", screen)].set_text(f"{self._main.finish_time: 0.2f}", self.TIME_FONT, self._main.colour_dict["Text"])
		
		#draw the minecount box and draw the minecount
		self.box_dict[("minecount_box", screen)].draw()
		if self._main.start_active:
			minecount = "N/A"
		else:
			minecount = str(self._main.minecount)
		self.box_dict[("minecount_box", screen)].set_text(minecount, self.FONT, self._main.colour_dict["Text"])
		
		#disaply the back button
		self.button_dict[("back_button", screen)][0].draw()
		self.button_dict[("back_button", screen)][0].set_text("<-", self.FONT, self._main.colour_dict["Text"])
		
		#disaply the exit button
		self.button_dict[("exit_button", screen)][0].draw()
		
		#display the reset button
		self.button_dict[("reset_button", screen)][0].update()
		self.button_dict[("reset_button", screen)][0].set_image(resource_path("MainPrograms/reset.png"))
		
		#display the board bounding box
		self.box_dict[("board_box", screen)].draw()
		
		#if the user has died, indicate to the user
		if not self._main.alive and not self._main.start_active:
			text = self.create_object(BoundingBox,
									  (100 * self.POINT_SIZE, 20 * self.POINT_SIZE),
									  self.WIN, 0, 0, self.POINT_SIZE, self._main.colour_dict["Border"], 0, self._main.colour_dict["Background"])
			text.set_text("You died :(", self.FONT, self._main.colour_dict["Text"])
		
		#if the user has won, indicate to the user
		elif self._main.won:
			text = self.create_object(BoundingBox,
									  (100 * self.POINT_SIZE, 20 * self.POINT_SIZE),
									  self.WIN, 0, 0, self.POINT_SIZE, self._main.colour_dict["Border"], 0, self._main.colour_dict["Background"])
			text.set_text("You won :)", self.FONT, self._main.colour_dict["Text"])
		
		#if the user is yet to select a starting tile, indicate to the user
		elif self._main.start_active:
			text = self.create_object(BoundingBox,
									  (100 * self.POINT_SIZE, 20 * self.POINT_SIZE),
									  self.WIN, 0, 0, self.POINT_SIZE, self._main.colour_dict["Border"], 0, self._main.colour_dict["Background"])
			text.set_text("Please select starting tile", self.FONT, self._main.colour_dict["Text"])
	
	def move_to_generator_select(self):
		"""
			Moves to the screen for the level selection

			Inputs:
				- None
			Outputs:
				- None

		"""
		# sets the background to white at the start of the program
		self.WIN.fill(self._main.colour_dict["Background"])
		
		self.unfocus_boxes()
		
		# display the title
		text = self.create_object(BoundingBox,
								  (100 * self.POINT_SIZE, 10 * self.POINT_SIZE),
								  self.WIN, 0, 0, self.POINT_SIZE, self._main.colour_dict["Border"], 0, self._main.colour_dict["Background"])
		text.set_text("Custom", pygame.font.Font(resource_path("MainPrograms/Fonts/mine-sweeper.ttf"), int(self.POINT_SIZE * 7)), self._main.colour_dict["Text"])
		pygame.display.update()
		
		# defines and creates a start button
		self.button_dict[("start_button", "generator_select")] = (self.create_object(Button,
																					 (85 * self.POINT_SIZE, 90 * self.POINT_SIZE),
																					 self.WIN, self.POINT_SIZE, (30 * self.POINT_SIZE), (10 * self.POINT_SIZE), self._main.colour_dict["Yes"], "start_button"),
																  self.move_to_gameplay_screen)
		self.button_dict[("start_button", "generator_select")][0].set_text("START", self.TILE_FONT, self._main.colour_dict["Text"])
		
		# defines and draws an exit button to be used to close the game
		self.button_dict[("exit_button", "generator_select")]: Button = (self.create_object(Button,
																							(self.WIDTH - (5 * self.POINT_SIZE) - self.POINT_SIZE, self.POINT_SIZE),
																							self.WIN, self.POINT_SIZE, (5 * self.POINT_SIZE), (5 * self.POINT_SIZE), self._main.colour_dict["No"], "exit_button"),
																		 self.close_game)
		# defines and creates a back button
		self.button_dict[("back_button", "generator_select")]: Button = (self.create_object(Button,
																							(self.POINT_SIZE, self.POINT_SIZE),
																							self.WIN, self.POINT_SIZE, (5 * self.POINT_SIZE), (5 * self.POINT_SIZE), self._main.colour_dict["Back"], "back_button"),
																		 self.move_to_gameplay_options_screen)
		self.button_dict[("back_button", "generator_select")][0].set_text("<-", self.FONT, self._main.colour_dict["Text"])
		
		#define and draw offset button if the generator needs it.
		self.button_dict[("offset", "generator_select")] = (self.create_object(Button,
																			   (150 * self.POINT_SIZE, 20 * self.POINT_SIZE),
																			   self.WIN, self.POINT_SIZE, (30 * self.POINT_SIZE), (10 * self.POINT_SIZE), self._main.colour_dict["Border"], "offset", 3, self._main.colour_dict["Background"], draw=False),
															self.move_to_offset_screen)
		
		if ("seed", "generator_select") not in self.text_box_dict.keys():
			#create all the objects
			self.text_box_dict[("seed", "generator_select")] = self.create_object(TextInputBox,
																				  (150 * self.POINT_SIZE, 40 * self.POINT_SIZE),
																				  self.WIN, (30 * self.POINT_SIZE), (10 * self.POINT_SIZE), self.POINT_SIZE, self._main.colour_dict["Border"], 3, "seed", self._main.colour_dict["Background"])
			self.text_box_dict[("minecount", "generator_select")] = self.create_object(TextInputBox,
																					   (110 * self.POINT_SIZE, 40 * self.POINT_SIZE),
																					   self.WIN, (30 * self.POINT_SIZE), (10 * self.POINT_SIZE), self.POINT_SIZE, self._main.colour_dict["Border"], 3, "minecount", self._main.colour_dict["Background"])
			self.text_box_dict[("spaces", "generator_select")] = self.create_object(TextInputBox,
																					(70 * self.POINT_SIZE, 20 * self.POINT_SIZE),
																					self.WIN, (30 * self.POINT_SIZE), (10 * self.POINT_SIZE), self.POINT_SIZE, self._main.colour_dict["Border"], 3, "spaces", self._main.colour_dict["Background"], draw=False)
			self.text_box_dict[("difficulty", "generator_select")] = self.create_object(TextInputBox,
																						(110 * self.POINT_SIZE, 20 * self.POINT_SIZE),
																						self.WIN, (30 * self.POINT_SIZE), (10 * self.POINT_SIZE), self.POINT_SIZE, self._main.colour_dict["Border"], 3, "difficulty", self._main.colour_dict["Background"], draw=False)
			self.text_box_dict[("rows", "generator_select")] = self.create_object(TextInputBox,
																				  (30 * self.POINT_SIZE, 40 * self.POINT_SIZE),
																				  self.WIN, (30 * self.POINT_SIZE), (10 * self.POINT_SIZE), self.POINT_SIZE, self._main.colour_dict["Border"], 3, "rows", self._main.colour_dict["Background"])
			self.text_box_dict[("cols", "generator_select")] = self.create_object(TextInputBox,
																				  (70 * self.POINT_SIZE, 40 * self.POINT_SIZE),
																				  self.WIN, (30 * self.POINT_SIZE), (10 * self.POINT_SIZE), self.POINT_SIZE, self._main.colour_dict["Border"], 3, "cols", self._main.colour_dict["Background"])
			
			#gamemode options, as we need a dropdown option for each one
			gamemodes = ["Standard", "Puzzle", "Space", "Chain", "Offset", "Offset Puzzle"]
			self.dropdown_dict[("gamemode", "generator_select")] = (self.create_object(DropdownBox,
																					   (30 * self.POINT_SIZE, 20 * self.POINT_SIZE),
																					   self.WIN, (30 * self.POINT_SIZE), (10 * self.POINT_SIZE), self.POINT_SIZE, self._main.colour_dict["Border"], 3, "gamemode", self._main.colour_dict["Background"]),
																	*(DropdownOption(self.WIN, (30 * self.POINT_SIZE), (10 * self.POINT_SIZE), self.POINT_SIZE, self._main.colour_dict["Border"], 1, name, self._main.colour_dict["Background"]) for name in gamemodes))
			
			# display the name of the gamemode according to its length
			text = self.dropdown_dict[("gamemode", "generator_select")][0].get_name().capitalize()
			if len(self._main.generator) < 10:
				self.dropdown_dict[("gamemode", "generator_select")][0].set_text(text, font.Font(resource_path("MainPrograms/Fonts/Roboto/static/Roboto-Bold.ttf"), int(self.POINT_SIZE * 5.5)), self._main.colour_dict["Text"])
			else:
				self.dropdown_dict[("gamemode", "generator_select")][0].set_text(text, font.Font(resource_path("MainPrograms/Fonts/Roboto/static/Roboto-Bold.ttf"), int(self.POINT_SIZE * 4.5)), self._main.colour_dict["Text"])
			self.box_dict[("info", "generator_select")] = self.create_object(BoundingBox,
																			 (30 * self.POINT_SIZE, 55 * self.POINT_SIZE),
																			 self.WIN, (150 * self.POINT_SIZE), (30 * self.POINT_SIZE), self.POINT_SIZE, self._main.colour_dict["Border"], 4, self._main.colour_dict["Background"])
		else:
			#draw the options that are not text boxes
			self.dropdown_dict[("gamemode", "generator_select")][0].draw()
			
			# display the name of the gamemode according to its length
			text = self.dropdown_dict[("gamemode", "generator_select")][0].get_current_option().capitalize()
			if len(self._main.generator) < 10:
				self.dropdown_dict[("gamemode", "generator_select")][0].set_text(text, font.Font(resource_path("MainPrograms/Fonts/Roboto/static/Roboto-Bold.ttf"), int(self.POINT_SIZE * 5.5)), self._main.colour_dict["Text"])
			else:
				self.dropdown_dict[("gamemode", "generator_select")][0].set_text(text, font.Font(resource_path("MainPrograms/Fonts/Roboto/static/Roboto-Bold.ttf"), int(self.POINT_SIZE * 4.5)), self._main.colour_dict["Text"])
			
			#initialise the info text
			self.box_dict[("info", "generator_select")].draw()
			self.box_dict[("info", "generator_select")].set_text_left_just("", font.Font(resource_path("MainPrograms/Fonts/Roboto/static/Roboto-Bold.ttf"), int(self.POINT_SIZE * 3)), colour=self._main.colour_dict["Text"])
		
		#update objects to see if they should be active or not depending on the gamemode
		#offset
		if "Offset" in self._main.generator:
			#set active
			self.button_dict[("offset", "generator_select")][0].set_active(True)
			
			#draw the button to the screen and display its text
			self.button_dict[("offset", "generator_select")][0].draw()
			self.button_dict[("offset", "generator_select")][0].set_text("Offset", self.TEXTBOX_FONT, self._main.colour_dict["Text"])
		else:
			#set inactive
			self.button_dict[("offset", "generator_select")][0].set_active(False)
		
		#difficulty
		if "puzzle" in self._main.generator.lower():
			#set active
			self.text_box_dict[("difficulty", "generator_select")].set_active(True)
		else:
			#set inactive
			self.text_box_dict[("difficulty", "generator_select")].set_active(False)
		
		#spaces
		if any(name in self._main.generator for name in ["Space", "Offset", "Puzzle"]):
			#set active
			self.text_box_dict[("spaces", "generator_select")].set_active(True)
		else:
			#set inactive
			self.text_box_dict[("spaces", "generator_select")].set_active(False)
		
		#draw all the text_boxes
		for key in self.text_box_dict.keys():
			if key[1] != "generator_select":
				continue
			
			#store the text box for future use
			text_box = self.text_box_dict[key]
			
			#if the box is not active, skip
			if not text_box.get_active():
				continue
			
			#draw
			text_box.draw()
			
			#display the name according to the length of its text
			if len(text_box.get_text()) == 0:
				key_name: str = key[0].capitalize()
				text_box.set_text(key_name, self.TEXTBOX_FONT, self._main.colour_dict["Text"])
			elif len(text_box.get_text()) < 5:
				text_box.display_text(self.TEXTBOX_FONT, self._main.colour_dict["Text"])
			else:
				text_box.display_text(self.TEXTBOX_FONT_2, self._main.colour_dict["Text"])
		
		#get all the dropdown options
		for dropdown_name in self.dropdown_dict.keys():
			if dropdown_name[1] != "generator_select":
				continue
			
			_, *dropdown_options = self.dropdown_dict[dropdown_name]
			
			#set their positions, and make sure they are not visible
			for i in range(len(dropdown_options)):
				dropdown_option: DropdownOption = dropdown_options[i]
				dropdown_option.set_pos((30 * self.POINT_SIZE, 31 * self.POINT_SIZE + (11 * self.POINT_SIZE * i)))
				dropdown_option.set_visible(False)
		
		#get the minecount from the minecount box
		self._main.minecount = self._main.set_int_variable(self.text_box_dict[("minecount", "generator_select")].get_text())
		
		#clear the error text
		self._main.validator.set_error_text()
		
		#run all validation checks for the generator
		self._main.valid_minecount = self._main.validator.minecount(self._main.minecount, self._main.board_rows, self._main.board_cols, self._main.board_rows * self._main.board_cols, self._main.spaces, self._main.generator)
		self._main.valid_rows = self._main.validator.rows(self._main.board_rows, self._main.board_cols)
		self._main.valid_cols = self._main.validator.cols(self._main.board_rows, self._main.board_cols)
		if "puzzle" in self._main.generator.lower():
			self._main.valid_difficulty = self._main.validator.difficulty(self._main.difficulty)
		if "offset" in self._main.generator.lower():
			self._main.valid_offset = self._main.validator.offset(self._main.offset_directions)
		
		#start board generation if possible
		self._main.generate_board_early()
		
		# set the screen type
		self._main.screen = "generator_select"
	
	def move_to_offset_screen(self) -> None:
		"""
			Moves to the screen for the offset selection

			Inputs:
				- None
			Outputs:
				- None

		"""
		# sets the background to white at the start of the program
		self.WIN.fill(self._main.colour_dict["Background"])
		
		#clear focused condition
		self.unfocus_boxes()
		
		# defines and creates a start button
		self.button_dict[("exit_button", "offset")]: Button = (self.create_object(Button,
																				  (self.WIDTH - (5 * self.POINT_SIZE) - self.POINT_SIZE, self.POINT_SIZE),
																				  self.WIN, self.POINT_SIZE, (5 * self.POINT_SIZE), (5 * self.POINT_SIZE), self._main.colour_dict["No"], "exit_button"),
															   self.close_game)
		
		self.button_dict[("back_button", "offset")]: Button = (self.create_object(Button,
																				  (self.POINT_SIZE, self.POINT_SIZE),
																				  self.WIN, self.POINT_SIZE, (5 * self.POINT_SIZE), (5 * self.POINT_SIZE), self._main.colour_dict["Back"], "back_button"),
															   self.move_to_generator_select)
		self.button_dict[("back_button", "offset")][0].set_text("<-", self.FONT, self._main.colour_dict["Text"])
		
		# set screen type
		self._main.screen = "offset"
		self._main.offset_active = True
		self._main._ready = False
		
		# create the tile board
		# for each row
		for rows in range(5):
			# initialize a list to contain the tiles for that row
			row: list[Tile] = []
			
			# for each column
			for cols in range(5):
				# initialize, set the position and draw the tile
				tile = Tile(
					surface=self.WIN,
					tile_size=10 * self.POINT_SIZE,
					point_size=self.POINT_SIZE,
					border_colour=self._main.colour_dict["Border"],
					border_width=1,
					tile_coordinate=(rows, cols),
					rows=5,
					cols=5,
					text_colour_start=self._main.colour_dict["Tile start"],
					text_colour_end=self._main.colour_dict["Tile end"],
					background_colour=self._main.colour_dict["Background"])
				tile.set_pos((10 * self.POINT_SIZE * (cols + 7.5), 10 * self.POINT_SIZE * (rows + 3)))
				tile.draw()
				
				#if the tile was previously selected
				if (rows - 2, cols - 2) in self._main.offset_directions:
					tile.fill(self._main.colour_dict["Yes"])
				
				#add the tile to the row
				row.append(tile)
			#add the row to the tile board
			self.offset_tile_board.append(row)
		
		#draw the offset board box
		self.box_dict[("board_box", "offset")]: BoundingBox = self.create_object(BoundingBox,
																				 (75 * self.POINT_SIZE, 30 * self.POINT_SIZE),
																				 self.WIN, (50 * self.POINT_SIZE), (50 * self.POINT_SIZE), self.POINT_SIZE, self._main.colour_dict["Border"], 5, self._main.colour_dict["Background"])
		
		#set the middle tile to black
		self.offset_tile_board[2][2].fill(self._main.colour_dict["Border"])
	
	def update_error_box(self, current_text: set[str], location: str = "generator_select") -> None:
		"""
			Displays all error lines in the generator select screen
			
			Inputs:
				- current_text: the text to display
				- location: the screen of the error info object
		
		"""
		#clear the info box
		self.box_dict[("info", location)].update()
		
		i = 0
		for line in current_text:
			
			#display each line that is not blank
			if line == "":
				continue
			self.box_dict[("info", location)].set_text_left_just(line, font.Font(resource_path("MainPrograms/Fonts/Roboto/static/Roboto-Bold.ttf"), int(self.POINT_SIZE * 3)), 5 * i * self.POINT_SIZE, colour=self._main.colour_dict["No"])
			i += 1
	
	def update_login_error_box(self, current_text: set[str], location: str = "generator_select") -> None:
		"""
			Displays the errors on the login or create account screens.

			Inputs:
				- current_text: the errors to display
				- location: the screen to display the error on
			Outputs:
				- None
		"""
		
		# clear the error box
		self.box_dict[("info", location)].update()
		
		# for each error
		for line in current_text:
			
			# if the error line is blank, skip
			if line == "":
				continue
			
			# display the error
			self.box_dict[("info", location)].set_text(line, font.Font(resource_path("MainPrograms/Fonts/Roboto/static/Roboto-Bold.ttf"), int(self.POINT_SIZE * 3)), colour=(255, 0, 0))
			break
	
	def move_to_first_loading_screen(self, error: bool) -> tuple[list[mp.Process], mp.Queue, mp.Queue]:
		"""
			Move to the loading screen when the user first boots the game
			
			Inputs:
				- None
			Outputs:
				- workers: a list of all the worker processes
				- task_queue: the queue the workers will look at to get tasks
				- result_queue: the queue the workers will return values to
		 
		"""
		
		#clear the surface
		self.WIN.fill(self._main.colour_dict["Background"])
		
		#display the title
		text = self.create_object(BoundingBox,
								  (100 * self.POINT_SIZE, 30 * self.POINT_SIZE),
								  self.WIN, 0, 0, self.POINT_SIZE, self._main.colour_dict["Border"], 0, self._main.colour_dict["Background"])
		text.set_text("MINECELLS", pygame.font.Font(resource_path("MainPrograms/Fonts/mine-sweeper.ttf"), int(self.POINT_SIZE * 8)), self._main.colour_dict["Text"])
		pygame.display.update()
		
		# If this game was opened after an error
		if error:
			#indicate to the user
			text = self.create_object(BoundingBox,
									  (100 * self.POINT_SIZE, 60 * self.POINT_SIZE),
									  self.WIN, 0, 0, self.POINT_SIZE, self._main.colour_dict["Border"], 0, self._main.colour_dict["Background"])
			text.set_text("An error occurred", pygame.font.Font(resource_path("MainPrograms/Fonts/Roboto/Static/Roboto-Bold.ttf"), int(self.POINT_SIZE * 3)), self._main.colour_dict["No"])
			pygame.display.update()
		
		#initialize the parallel processing
		workers, task_queue, result_queue = self._main.board_gen_hub.init_parallel()
		
		#if the database has not been created, initialize the level database
		if not self._main.level_manager.check_table_exists():
			self._main.level_manager.init_database_level()
			self._main.level_manager.init_database_tutorial()
		
		#move to level select screen
		self.move_to_home_screen()
		
		#return parallel values
		return workers, task_queue, result_queue
	
	def move_to_home_screen(self) -> None:
		"""
			Move to the home screen when the user first loads into the game

			Inputs:
				- None
			Outputs:
				- None
		"""
		# clear the surface
		self.WIN.fill(self._main.colour_dict["Background"])
		
		#clear the focused condition of the boxes
		self.unfocus_boxes()
		
		#set the current screen to home
		self._main.screen = "home"
		
		# display the title
		text = self.create_object(BoundingBox,
								  (100 * self.POINT_SIZE, 30 * self.POINT_SIZE),
								  self.WIN, 0, 0, self.POINT_SIZE, self._main.colour_dict["Border"], 0, self._main.colour_dict["Background"])
		text.set_text("MINECELLS", pygame.font.Font(resource_path("MainPrograms/Fonts/mine-sweeper.ttf"), int(self.POINT_SIZE * 8)), self._main.colour_dict["Text"])
		pygame.display.update()
		
		# display the play button to allow the user to edit their options
		self.button_dict[("options", "home")] = (self.create_object(Button,
																	(60 * self.POINT_SIZE, 50 * self.POINT_SIZE),
																	self.WIN, self.POINT_SIZE, (20 * self.POINT_SIZE), (20 * self.POINT_SIZE), self._main.colour_dict["Yes"], "options"),
												 self.move_to_options)
		self.button_dict[("options", "home")][0].set_text("Options", pygame.font.Font(resource_path("MainPrograms/Fonts/mine-sweeper.ttf"), int(self.POINT_SIZE * 2.5)), self._main.colour_dict["Text"])
		
		#display the play button to allow the user to start the game
		self.button_dict[("play_button", "home")] = (self.create_object(Button,
																		(90 * self.POINT_SIZE, 50 * self.POINT_SIZE),
																		self.WIN, self.POINT_SIZE, (20 * self.POINT_SIZE), (20 * self.POINT_SIZE), self._main.colour_dict["Yes"], "play_button"),
													 self.move_to_gameplay_options_screen)
		self.button_dict[("play_button", "home")][0].set_text("Play", pygame.font.Font(resource_path("MainPrograms/Fonts/mine-sweeper.ttf"), int(self.POINT_SIZE * 4)), self._main.colour_dict["Text"])
		
		#check if a user is logged in
		if self._main.validator.get_user_logged_in():
			# display the play button to allow the user to move to the account screen
			self.button_dict[("account", "home")] = (self.create_object(Button,
																		(120 * self.POINT_SIZE, 50 * self.POINT_SIZE),
																		self.WIN, self.POINT_SIZE, (20 * self.POINT_SIZE), (20 * self.POINT_SIZE), self._main.colour_dict["Yes"], "account"),
													 self.move_to_account)
			self.button_dict[("account", "home")][0].set_text("Account", pygame.font.Font(resource_path("MainPrograms/Fonts/mine-sweeper.ttf"), int(self.POINT_SIZE * 2.5)), self._main.colour_dict["Text"])
			
			#if there is a login button, delete it to prevent it from overlapping with the log out button
			if ("login", "home") in self.button_dict.keys():
				del self.button_dict[("login", "home")]
		else:
			# display the play button to allow the user to login
			self.button_dict[("login", "home")] = (self.create_object(Button,
																	  (120 * self.POINT_SIZE, 50 * self.POINT_SIZE),
																	  self.WIN, self.POINT_SIZE, (20 * self.POINT_SIZE), (20 * self.POINT_SIZE), self._main.colour_dict["Yes"], "login"),
												   self.move_to_login)
			self.button_dict[("login", "home")][0].set_text("Log in", pygame.font.Font(resource_path("MainPrograms/Fonts/mine-sweeper.ttf"), int(self.POINT_SIZE * 3)), self._main.colour_dict["Text"])
			
			# if there is a log out button, delete it to prevent it from overlapping with the login button
			if ("account", "home") in self.button_dict.keys():
				del self.button_dict[("account", "home")]
		
		# defines and creates a start button
		self.button_dict[("exit_button", "home")]: Button = (self.create_object(Button,
																				(self.WIDTH - (5 * self.POINT_SIZE) - self.POINT_SIZE, self.POINT_SIZE),
																				self.WIN, self.POINT_SIZE, (5 * self.POINT_SIZE), (5 * self.POINT_SIZE), self._main.colour_dict["No"], "exit_button"),
															 self.close_game)
	
	def log_out(self) -> None:
		"""
			Log out of the current account and return to the home screen
			
			Inputs:
				- None
			Outputs:
				- None
		"""
		self._main.validator.log_out()
		self.move_to_home_screen()
	
	def move_to_account(self) -> None:
		"""
			Moves to the account screen

			Inputs:
				- None
			Outputs:
				- None
		"""
		# clear the surface
		self.WIN.fill(self._main.colour_dict["Background"])
		
		#makes sure none of the boxes are focused when moving between screens
		self.unfocus_boxes()
		
		#change the current screen to the account screen
		self._main.screen = "account"
		
		#display the scores title
		self.box_dict[("scores", "account")] = self.create_object(BoundingBox,
																  (95 * self.POINT_SIZE, 5 * self.POINT_SIZE),
																  self.WIN, (10 * self.POINT_SIZE), (10 * self.POINT_SIZE), self.POINT_SIZE, self._main.colour_dict["Background"], 4, self._main.colour_dict["Background"])
		self.box_dict[("scores", "account")].set_text("Scores", font.Font(resource_path("MainPrograms/Fonts/Roboto/static/Roboto-Bold.ttf"), int(self.POINT_SIZE * 7)), colour=self._main.colour_dict["Text"])
		
		#display the custom name
		self.box_dict[("custom_info", "account")] = self.create_object(BoundingBox,
																	   (25 * self.POINT_SIZE, 20 * self.POINT_SIZE),
																	   self.WIN, (10 * self.POINT_SIZE), (7 * self.POINT_SIZE), self.POINT_SIZE, self._main.colour_dict["Background"], 4, self._main.colour_dict["Background"])
		self.box_dict[("custom_info", "account")].set_text_left_just("Custom:", font.Font(resource_path("MainPrograms/Fonts/Roboto/static/Roboto-Bold.ttf"), int(self.POINT_SIZE * 5)), colour=self._main.colour_dict["Text"], offset=self.POINT_SIZE)
		
		#display the custom score
		custom_score = self._main.validator.get_score()
		self.box_dict[("custom_score", "account")] = self.create_object(BoundingBox,
																		(50 * self.POINT_SIZE, 20 * self.POINT_SIZE),
																		self.WIN, (25 * self.POINT_SIZE), (7 * self.POINT_SIZE), self.POINT_SIZE, self._main.colour_dict["Border"], 4, self._main.colour_dict["Background"])
		self.box_dict[("custom_score", "account")].set_text(str(custom_score), pygame.font.Font(resource_path("MainPrograms/Fonts/Roboto/static/Roboto-Bold.ttf"), int(self.POINT_SIZE * min(6.0, 7 - math.log2(max(1.0, 0.75 * len(str(custom_score))))))), self._main.colour_dict["Text"])
		
		#gets the times for all the levels from the database
		levels_times = self._main.validator.get_level_times()
		
		# load all the level times from the database
		level_times: dict = self._main.validator.get_level_times()
		
		#if all levels other than level 6 have been completed
		if all((level_times[level] != -1 or level == "Level 6") for level in level_times.keys()):
			level_time = levels_times["Level 6"]
			
			#set to N/A if level not completed
			if level_time == -1:
				level_time = "N/A"
			
			# else convert to string, and add s to indicate seconds
			else:
				level_time = str(level_time) + "s"
			
			# display level name
			self.box_dict[(f"level_6_info", "account")] = self.create_object(BoundingBox,
																			 (75 * self.POINT_SIZE, 75 * self.POINT_SIZE),
																			 self.WIN, (10 * self.POINT_SIZE), (7 * self.POINT_SIZE), self.POINT_SIZE, self._main.colour_dict["Background"], 4, self._main.colour_dict["Background"])
			self.box_dict[(f"level_6_info", "account")].set_text_left_just("Level 6:", font.Font(resource_path("MainPrograms/Fonts/Roboto/static/Roboto-Bold.ttf"), int(self.POINT_SIZE * 5)), colour=self._main.colour_dict["Text"], offset=self.POINT_SIZE)
			
			# display level time
			self.box_dict[(f"level_6_time", "account")] = self.create_object(BoundingBox,
																			 (100 * self.POINT_SIZE, 75 * self.POINT_SIZE),
																			 self.WIN, (25 * self.POINT_SIZE), (7 * self.POINT_SIZE), self.POINT_SIZE, self._main.colour_dict["Border"], 4, self._main.colour_dict["Background"])
			self.box_dict[(f"level_6_time", "account")].set_text(level_time, pygame.font.Font(resource_path("MainPrograms/Fonts/Roboto/static/Roboto-Bold.ttf"), int(self.POINT_SIZE * min(6.0, 7 - math.log2(max(1.0, 0.75 * len(str(custom_score))))))), self._main.colour_dict["Text"])
		
		#for each (main) level
		for i in range(1, 6):
			
			#get the time for that level
			level_time = levels_times[f"Level {i}"]
			
			#if level has not been completed, set to N/A
			if level_time == -1:
				level_time = "N/A"
			
			#else convert to string, and add s to indicate seconds
			else:
				level_time = str(level_time) + "s"
			
			#display level name
			self.box_dict[(f"level_{i}_info", "account")] = self.create_object(BoundingBox,
																			   (100 * self.POINT_SIZE * (i % 2 == 1) + 25 * self.POINT_SIZE, 20 * self.POINT_SIZE + 20 * self.POINT_SIZE * (i // 2)),
																			   self.WIN, (10 * self.POINT_SIZE), (7 * self.POINT_SIZE), self.POINT_SIZE, self._main.colour_dict["Background"], 4, self._main.colour_dict["Background"])
			self.box_dict[(f"level_{i}_info", "account")].set_text_left_just(f"Level {i}:", font.Font(resource_path("MainPrograms/Fonts/Roboto/static/Roboto-Bold.ttf"), int(self.POINT_SIZE * 5)), colour=self._main.colour_dict["Text"], offset=self.POINT_SIZE)
			
			#display level time
			self.box_dict[(f"level_{i}_time", "account")] = self.create_object(BoundingBox,
																			   (100 * self.POINT_SIZE * (i % 2 == 1) + 50 * self.POINT_SIZE, 20 * self.POINT_SIZE + 20 * self.POINT_SIZE * (i // 2)),
																			   self.WIN, (25 * self.POINT_SIZE), (7 * self.POINT_SIZE), self.POINT_SIZE, self._main.colour_dict["Border"], 4, self._main.colour_dict["Background"])
			self.box_dict[(f"level_{i}_time", "account")].set_text(level_time, pygame.font.Font(resource_path("MainPrograms/Fonts/Roboto/static/Roboto-Bold.ttf"), int(self.POINT_SIZE * min(6.0, 7 - math.log2(max(1.0, 0.75 * len(str(custom_score))))))), self._main.colour_dict["Text"])
		
		# display the button to confirm the user wants to log out
		self.button_dict[("log_out", "account")] = (self.create_object(Button,
																	   (80 * self.POINT_SIZE, 90 * self.POINT_SIZE),
																	   self.WIN, self.POINT_SIZE, (40 * self.POINT_SIZE), (10 * self.POINT_SIZE), self._main.colour_dict["No"], "log_out"),
													self.log_out)
		self.button_dict[("log_out", "account")][0].set_text("Log Out", self.FONT, self._main.colour_dict["Text"])
		
		# defines and creates a back button
		self.button_dict[("back_button", "account")]: Button = (self.create_object(Button,
																				   (self.POINT_SIZE, self.POINT_SIZE),
																				   self.WIN, self.POINT_SIZE, (5 * self.POINT_SIZE), (5 * self.POINT_SIZE), self._main.colour_dict["Back"], "back_button"),
																self.move_to_home_screen)
		self.button_dict[("back_button", "account")][0].set_text("<-", self.FONT, self._main.colour_dict["Text"])
		
		# defines and creates an exit button
		self.button_dict[("exit_button", "account")]: Button = (self.create_object(Button,
																				   (self.WIDTH - (5 * self.POINT_SIZE) - self.POINT_SIZE, self.POINT_SIZE),
																				   self.WIN, self.POINT_SIZE, (5 * self.POINT_SIZE), (5 * self.POINT_SIZE), self._main.colour_dict["No"], "exit_button"),
																self.close_game)
	
	def move_to_gameplay_options_screen(self) -> None:
		"""
			Move to the gameplay options screen

			Inputs:
				- None
			Outputs:
				- None
		"""
		# clear the surface
		self.WIN.fill(self._main.colour_dict["Background"])
		
		#clear the focused condition
		self.unfocus_boxes()
		
		#set screen type to gameplay screen
		self._main.screen = "gameplay_options"
		
		# display the title
		text = self.create_object(BoundingBox,
								  (100 * self.POINT_SIZE, 10 * self.POINT_SIZE),
								  self.WIN, 0, 0, self.POINT_SIZE, self._main.colour_dict["Border"], 0, self._main.colour_dict["Background"])
		text.set_text("MINECELLS", pygame.font.Font(resource_path("MainPrograms/Fonts/mine-sweeper.ttf"), int(self.POINT_SIZE * 8)), self._main.colour_dict["Text"])
		pygame.display.update()
		
		# defines and displays a levels button
		self.button_dict[("tutorial_button", "gameplay_options")] = (self.create_object(Button,
																						(12.5 * self.POINT_SIZE, 20 * self.POINT_SIZE),
																						self.WIN, self.POINT_SIZE, (50 * self.POINT_SIZE), (80 * self.POINT_SIZE), tuple([max(0, int((3 / 5) * self._main.colour_dict["Yes"][i])) for i in range(3)]), "tutorial_button"),
																	 self.move_to_tutorial_screen)
		self.button_dict[("tutorial_button", "gameplay_options")][0].set_text("Tutorial", pygame.font.Font(resource_path("MainPrograms/Fonts/mine-sweeper.ttf"), int(self.POINT_SIZE * 4)), self._main.colour_dict["Text"])
		
		# defines and displays a levels button
		self.button_dict[("levels_button", "gameplay_options")] = (self.create_object(Button,
																					  (75 * self.POINT_SIZE, 20 * self.POINT_SIZE),
																					  self.WIN, self.POINT_SIZE, (50 * self.POINT_SIZE), (80 * self.POINT_SIZE), tuple([max(0, int((4 / 5) * self._main.colour_dict["Yes"][i])) for i in range(3)]), "levels_button"),
																   self.move_to_level_select_screen)
		self.button_dict[("levels_button", "gameplay_options")][0].set_text("Levels", pygame.font.Font(resource_path("MainPrograms/Fonts/mine-sweeper.ttf"), int(self.POINT_SIZE * 4)), self._main.colour_dict["Text"])
		
		# defines and displays a custom button
		self.button_dict[("custom_button", "gameplay_options")] = (self.create_object(Button,
																					  (137.5 * self.POINT_SIZE, 20 * self.POINT_SIZE),
																					  self.WIN, self.POINT_SIZE, (50 * self.POINT_SIZE), (80 * self.POINT_SIZE), self._main.colour_dict["Yes"], "custom_button"),
																   self.move_to_generator_select)
		self.button_dict[("custom_button", "gameplay_options")][0].set_text("Custom", pygame.font.Font(resource_path("MainPrograms/Fonts/mine-sweeper.ttf"), int(self.POINT_SIZE * 4)), self._main.colour_dict["Text"])
		
		# defines and creates a start button
		self.button_dict[("exit_button", "gameplay_options")]: Button = (self.create_object(Button,
																							(self.WIDTH - (5 * self.POINT_SIZE) - self.POINT_SIZE, self.POINT_SIZE),
																							self.WIN, self.POINT_SIZE, (5 * self.POINT_SIZE), (5 * self.POINT_SIZE), self._main.colour_dict["No"], "exit_button"),
																		 self.close_game)
		
		# defines and creates a back button
		self.button_dict[("back_button", "gameplay_options")]: Button = (self.create_object(Button,
																							(self.POINT_SIZE, self.POINT_SIZE),
																							self.WIN, self.POINT_SIZE, (5 * self.POINT_SIZE), (5 * self.POINT_SIZE), self._main.colour_dict["Back"], "back_button"),
																		 self.move_to_home_screen)
		self.button_dict[("back_button", "gameplay_options")][0].set_text("<-", self.FONT, self._main.colour_dict["Text"])
	
	def move_to_level_select_screen(self) -> None:
		"""
			Move to the level select screen

			Inputs:
				- None
			Outputs:
				- None
		"""
		# clear the surface
		self.WIN.fill(self._main.colour_dict["Background"])
		
		# clear the focused condition
		self.unfocus_boxes()
		
		#set screen type to level select
		self._main.screen = "level_select"
		
		# display the title
		text = self.create_object(BoundingBox,
								  (100 * self.POINT_SIZE, 10 * self.POINT_SIZE),
								  self.WIN, 0, 0, self.POINT_SIZE, self._main.colour_dict["Border"], 0, self._main.colour_dict["Background"])
		text.set_text("Level Select", pygame.font.Font(resource_path("MainPrograms/Fonts/mine-sweeper.ttf"), int(self.POINT_SIZE * 6)), self._main.colour_dict["Text"])
		pygame.display.update()
		
		#defines and creates buttons to enter each level
		self.button_dict[("level_one", "level_select")] = (self.create_object(Button,
																			  (9 * self.POINT_SIZE, 20 * self.POINT_SIZE),
																			  self.WIN, self.POINT_SIZE, (30 * self.POINT_SIZE), (80 * self.POINT_SIZE), tuple([max(0, int((3 / 5) * self._main.colour_dict["Yes"][i])) for i in range(3)]), "level_one"),
														   self.move_to_level_one)
		self.button_dict[("level_one", "level_select")][0].set_text("Level 1", pygame.font.Font(resource_path("MainPrograms/Fonts/mine-sweeper.ttf"), int(self.POINT_SIZE * 4)), self._main.colour_dict["Text"])
		
		self.button_dict[("level_two", "level_select")] = (self.create_object(Button,
																			  (47 * self.POINT_SIZE, 20 * self.POINT_SIZE),
																			  self.WIN, self.POINT_SIZE, (30 * self.POINT_SIZE), (80 * self.POINT_SIZE), tuple([max(0, int((7 / 10) * self._main.colour_dict["Yes"][i])) for i in range(3)]), "level_two"),
														   self.move_to_level_two)
		self.button_dict[("level_two", "level_select")][0].set_text("Level 2", pygame.font.Font(resource_path("MainPrograms/Fonts/mine-sweeper.ttf"), int(self.POINT_SIZE * 4)), self._main.colour_dict["Text"])
		
		self.button_dict[("level_three", "level_select")] = (self.create_object(Button,
																				(85 * self.POINT_SIZE, 20 * self.POINT_SIZE),
																				self.WIN, self.POINT_SIZE, (30 * self.POINT_SIZE), (80 * self.POINT_SIZE), tuple([max(0, int((4 / 5) * self._main.colour_dict["Yes"][i])) for i in range(3)]), "level_three"),
															 self.move_to_level_three)
		self.button_dict[("level_three", "level_select")][0].set_text("Level 3", pygame.font.Font(resource_path("MainPrograms/Fonts/mine-sweeper.ttf"), int(self.POINT_SIZE * 4)), self._main.colour_dict["Text"])
		
		self.button_dict[("level_four", "level_select")] = (self.create_object(Button,
																			   (123 * self.POINT_SIZE, 20 * self.POINT_SIZE),
																			   self.WIN, self.POINT_SIZE, (30 * self.POINT_SIZE), (80 * self.POINT_SIZE), tuple([max(0, int((9 / 10) * self._main.colour_dict["Yes"][i])) for i in range(3)]), "level_four"),
															self.move_to_level_four)
		self.button_dict[("level_four", "level_select")][0].set_text("Level 4", pygame.font.Font(resource_path("MainPrograms/Fonts/mine-sweeper.ttf"), int(self.POINT_SIZE * 4)), self._main.colour_dict["Text"])
		
		self.button_dict[("level_five", "level_select")] = (self.create_object(Button,
																			   (161 * self.POINT_SIZE, 20 * self.POINT_SIZE),
																			   self.WIN, self.POINT_SIZE, (30 * self.POINT_SIZE), (80 * self.POINT_SIZE), self._main.colour_dict["Yes"], "level_five"),
															self.move_to_level_five)
		self.button_dict[("level_five", "level_select")][0].set_text("Level 5", pygame.font.Font(resource_path("MainPrograms/Fonts/mine-sweeper.ttf"), int(self.POINT_SIZE * 4)), self._main.colour_dict["Text"])
		
		#load all the level times from the database
		level_times: dict = self._main.validator.get_level_times()
		
		#if the user has completed all the main 5 levels, unlock level 6
		if all((level_times[level] != -1 or level == "Level 6") for level in level_times.keys()):
			self.button_dict[("level_six_screen", "level_select")] = (self.create_object(Button,
																						 (193 * self.POINT_SIZE, 57.5 * self.POINT_SIZE),
																						 self.WIN, self.POINT_SIZE, (5 * self.POINT_SIZE), (5 * self.POINT_SIZE), self._main.colour_dict["Back"], "level_six_screen"),
																	  self.move_to_level_six_screen)
			self.button_dict[("level_six_screen", "level_select")][0].set_text("?", pygame.font.Font(resource_path("MainPrograms/Fonts/mine-sweeper.ttf"), int(self.POINT_SIZE * 4)), self._main.colour_dict["Text"])
		
		# defines and creates a start button
		self.button_dict[("exit_button", "level_select")]: Button = (self.create_object(Button,
																						(self.WIDTH - (5 * self.POINT_SIZE) - self.POINT_SIZE, self.POINT_SIZE),
																						self.WIN, self.POINT_SIZE, (5 * self.POINT_SIZE), (5 * self.POINT_SIZE), self._main.colour_dict["No"], "exit_button"),
																	 self.close_game)
		# defines and creates a back button
		self.button_dict[("back_button", "level_select")]: Button = (self.create_object(Button,
																						(self.POINT_SIZE, self.POINT_SIZE),
																						self.WIN, self.POINT_SIZE, (5 * self.POINT_SIZE), (5 * self.POINT_SIZE), self._main.colour_dict["Back"], "back_button"),
																	 self.move_to_gameplay_options_screen)
		self.button_dict[("back_button", "level_select")][0].set_text("<-", self.FONT, self._main.colour_dict["Text"])
	
	def move_to_level_six_screen(self) -> None:
		"""
			Move to the screen for the user to select the final boss

			Inputs:
				- None
			Outputs:
				- None
		"""
		# clear the surface
		self.WIN.fill(self._main.colour_dict["Background"])
		
		#set the screen to the level 6 screen
		self._main.screen = "level_six"
		
		# display the title
		text = self.create_object(BoundingBox,
								  (100 * self.POINT_SIZE, 10 * self.POINT_SIZE),
								  self.WIN, 0, 0, self.POINT_SIZE, self._main.colour_dict["Border"], 0, self._main.colour_dict["Background"])
		text.set_text("Level Select", pygame.font.Font(resource_path("MainPrograms/Fonts/mine-sweeper.ttf"), int(self.POINT_SIZE * 6)), self._main.colour_dict["Text"])
		pygame.display.update()
		
		#defines and creates the button for the final boss
		self.button_dict[("final_boss", "level_six")] = (self.create_object(Button,
																			(75 * self.POINT_SIZE, 20 * self.POINT_SIZE),
																			self.WIN, self.POINT_SIZE, (50 * self.POINT_SIZE), (80 * self.POINT_SIZE), self._main.colour_dict["Yes"], "final_boss"),
														 self.move_to_final_boss)
		self.button_dict[("final_boss", "level_six")][0].set_text("Final Boss", pygame.font.Font(resource_path("MainPrograms/Fonts/mine-sweeper.ttf"), int(self.POINT_SIZE * 4)), self._main.colour_dict["Text"])
		
		# defines and creates an exit button
		self.button_dict[("exit_button", "level_six")]: Button = (self.create_object(Button,
																					 (self.WIDTH - (5 * self.POINT_SIZE) - self.POINT_SIZE, self.POINT_SIZE),
																					 self.WIN, self.POINT_SIZE, (5 * self.POINT_SIZE), (5 * self.POINT_SIZE), self._main.colour_dict["No"], "exit_button"),
																  self.close_game)
		# defines and creates a back button
		self.button_dict[("back_button", "level_six")]: Button = (self.create_object(Button,
																					 (self.POINT_SIZE, self.POINT_SIZE),
																					 self.WIN, self.POINT_SIZE, (5 * self.POINT_SIZE), (5 * self.POINT_SIZE), self._main.colour_dict["Back"], "back_button"),
																  self.move_to_level_select_screen)
		self.button_dict[("back_button", "level_six")][0].set_text("<-", self.FONT, self._main.colour_dict["Text"])
	
	def move_to_level(self, level: int) -> None:
		"""
			Moves to the screen for the relevant level
			
			Inputs:
				- level: the level the user will play
			Outputs:
				- None
		"""
		
		#clear the background
		self.WIN.fill(self._main.colour_dict["Background"])
		
		# store the board and revealed tiles
		if level == 10:
			self._main.board, self._main.revealed_tiles = self._main.level_manager.get_tutorial(10)
		else:
			self._main.board, self._main.revealed_tiles = self._main.level_manager.get_level(level)
		
		#rows and columns
		self._main.board_rows = len(self._main.board)
		self._main.board_cols = len(self._main.board[0])
		
		#minecount
		self._main.minecount = self._main.get_current_minecount(self._main.board)
		
		#store initial minecount
		self._main.start_minecount = self._main.minecount
		
		#set default values for these three, as they are not needed for the levels
		self._main.spaces = 0
		self._main.difficulty = 1
		self._main.seed = f"Level {level}"
		
		#initialize the board surface dimensions
		self._main.tile_surface_dims = (10 * self._main.board_cols * self.POINT_SIZE, 10 * self._main.board_rows * self.POINT_SIZE)
		
		# draw all the tiles
		self.tile_board = []
		
		# generate the dimensions of the tile surface based on the board size
		self._main.tile_surface_dims = (10 * self._main.board_cols * self.POINT_SIZE, 10 * self._main.board_rows * self.POINT_SIZE)
		
		# draw all the tiles
		self.tile_board = []
		
		# create the tile surface
		self._main.tile_surface = pygame.Surface((10 * self._main.board_cols * self.POINT_SIZE, 10 * self._main.board_rows * self.POINT_SIZE))
		
		# set it to the background colour
		self._main.tile_surface.fill(self._main.colour_dict["Background"])
		
		# clear the zoomed tile surface to indicate the surface hasn't been zoomed in or out yet
		self._main.zoomed_tile_surface = None
		
		# set zoom and offset to default values
		self._main.tile_surface_zoom = 1
		self._main.tile_surface_offset = (5 * self._main.board_cols * self.POINT_SIZE - 100 * self.POINT_SIZE, 5 * self._main.board_rows * self.POINT_SIZE - 65 * self.POINT_SIZE)
		
		# create the tile board
		# for each row
		for rows in range(self._main.board_rows):
			# initialize a list to contain the tiles for that row
			row: list[Tile] = []
			
			# for each column
			for cols in range(self._main.board_cols):
				# initialize, set the position and draw the tile
				tile = Tile(
					surface=self._main.tile_surface,
					tile_size=10 * self.POINT_SIZE,
					point_size=self.POINT_SIZE,
					border_colour=self._main.colour_dict["Border"],
					border_width=1,
					tile_coordinate=(rows, cols),
					rows=self._main.board_rows,
					cols=self._main.board_cols,
					text_colour_start=self._main.colour_dict["Tile start"],
					text_colour_end=self._main.colour_dict["Tile end"],
					background_colour=self._main.colour_dict["Background"])
				tile.set_pos((10 * self.POINT_SIZE * cols, 10 * self.POINT_SIZE * rows))
				tile.draw()
				
				# set its value to be empty
				tile.set_value(-2)
				
				# add it to the row
				row.append(tile)
			# add the row to the tile board
			self.tile_board.append(row)
		
		# display the board on the screen
		self.WIN.blit(self._main.tile_surface, (-self._main.tile_surface_offset[0], -self._main.tile_surface_offset[1]))
		
		# cover up the parts of the screen that are not the board to prevent the board from leaving the intended box
		# top
		cover = BoundingBox(self.WIN, 60 * self.POINT_SIZE, 200 * self.POINT_SIZE, self.POINT_SIZE, self._main.colour_dict["Background"], 0, self._main.colour_dict["Background"])
		cover.update()
		# bottom
		cover.set_pos((140 * self.POINT_SIZE, 0))
		cover.update()
		# left
		cover = BoundingBox(self.WIN, 200 * self.POINT_SIZE, 25 * self.POINT_SIZE, self.POINT_SIZE, self._main.colour_dict["Background"], 0, self._main.colour_dict["Background"])
		cover.set_pos((0, 0))
		cover.update()
		# right
		cover.set_pos((0, 105 * self.POINT_SIZE))
		cover.update()
		
		# defines and draws an exit button to be used to close the game
		self.button_dict[("exit_button", "gameplay")]: Button = (self.create_object(Button,
																					(self.WIDTH - (5 * self.POINT_SIZE) - self.POINT_SIZE, self.POINT_SIZE),
																					self.WIN, self.POINT_SIZE, (5 * self.POINT_SIZE), (5 * self.POINT_SIZE), self._main.colour_dict["No"], "exit_button", 0, self._main.colour_dict["Background"]),
																 self.close_game)
		
		# defines and draws a back button to be used to return to the previous screen
		self.button_dict[("back_button", "gameplay")]: Button = (self.create_object(Button,
																					(self.POINT_SIZE, self.POINT_SIZE),
																					self.WIN, self.POINT_SIZE, (5 * self.POINT_SIZE), (5 * self.POINT_SIZE), self._main.colour_dict["Back"], "back_button", 0, self._main.colour_dict["Background"]),
																 self.move_to_level_select_screen)
		self.button_dict[("back_button", "gameplay")][0].set_text("<-", self.FONT, self._main.colour_dict["Text"])
		
		#default (level 1)
		func = self.move_to_level_one
		
		#assign the correct function depending on the level for the reset button
		match level:
			case 2:
				func = self.move_to_level_two
			case 3:
				func = self.move_to_level_three
			case 4:
				func = self.move_to_level_four
			case 5:
				func = self.move_to_level_five
			case 6:
				func = self.move_to_final_boss
			case 10:
				func = self.move_to_tutorial_final_boss
		
		# defines and draws a back button to be used to return to the previous screen
		self.button_dict[("reset_button", "gameplay")]: Button = (self.create_object(Button,
																					 (75 * self.POINT_SIZE, 5 * self.POINT_SIZE),
																					 self.WIN, self.POINT_SIZE, (10 * self.POINT_SIZE), (10 * self.POINT_SIZE), self._main.colour_dict["Border"], "reset_button", 4, (255, 255, 255)),
																  func)
		self.button_dict[("reset_button", "gameplay")][0].update()
		self.button_dict[("reset_button", "gameplay")][0].set_image(resource_path("MainPrograms/reset.png"))
		
		# defines and draws a bounding box that will contain the minecount
		self.box_dict[("minecount_box", "gameplay")]: BoundingBox = self.create_object(BoundingBox,
																					   (95 * self.POINT_SIZE, 5 * self.POINT_SIZE),
																					   self.WIN, (10 * self.POINT_SIZE), (10 * self.POINT_SIZE), self.POINT_SIZE, self._main.colour_dict["Border"], 4, self._main.colour_dict["Background"])
		self.box_dict[("minecount_box", "gameplay")].set_text("N/A", self.FONT, self._main.colour_dict["Text"])
		
		# defines and draws a bounding box that will contain the board
		self.box_dict[("board_box", "gameplay")]: BoundingBox = self.create_object(BoundingBox,
																				   (60 * self.POINT_SIZE, 25 * self.POINT_SIZE),
																				   self.WIN, (80 * self.POINT_SIZE), (80 * self.POINT_SIZE), self.POINT_SIZE, self._main.colour_dict["Border"], 5, self._main.colour_dict["Background"])
		
		# defines and draws a bounding box that will display the time spent on the board
		self.box_dict[("time_box", "gameplay")]: BoundingBox = self.create_object(BoundingBox,
																				  (115 * self.POINT_SIZE, 5 * self.POINT_SIZE),
																				  self.WIN, (10 * self.POINT_SIZE), (10 * self.POINT_SIZE), self.POINT_SIZE, self._main.colour_dict["Border"], 4, self._main.colour_dict["Background"])
		self.box_dict[("time_box", "gameplay")].set_text("0.00", self.TIME_FONT, self._main.colour_dict["Text"])
		
		# generate a public board which represents what the user can see
		self._main.public_board = [[-2 for _ in range(self._main.board_cols)] for _ in range(self._main.board_rows)]
		
		# update the public board with the revealed tiles
		for rows, cols in self._main.revealed_tiles:
			self._main.public_board[rows][cols] = self._main.board[rows][cols]
			self.tile_board[rows][cols].set_value(self._main.board[rows][cols])
			self.tile_board[rows][cols].set_text(str(self._main.board[rows][cols]), pygame.font.Font(resource_path("MainPrograms/Fonts/mine-sweeper.ttf"), int(self.POINT_SIZE * 4)))
		
		# calculate how much to zoom to fit the entire board on the screen
		zoom_factor: float = min(80 / (10 * self._main.board_cols), 80 / (10 * self._main.board_rows))
		
		# zoom in/ out
		self._main.zoom(100 * self.POINT_SIZE, 65 * self.POINT_SIZE, zoom_multiplier=zoom_factor)
		
		# set screen type
		self._main.screen = "gameplay"
		self._main._ready = False
		self._main.start_active = False
		self._main.gameplay_active = True
		self._main.start_time = time.perf_counter()
		
		self.start_game(self._main.minecount)
		
		# user is alive and hasn't won
		self._main.alive = True
		self._main.won = False
		
		# if there is no zoomed surface, display the default
		if self._main.zoomed_tile_surface is None:
			self.WIN.blit(self._main.tile_surface, (-self._main.tile_surface_offset[0], -self._main.tile_surface_offset[1]))
		# else display the zoomed surface
		else:
			self.WIN.blit(self._main.zoomed_tile_surface, (-self._main.tile_surface_offset[0], -self._main.tile_surface_offset[1]))
		
		# redraw the gameplay screen
		self.redraw_gameplay_screen()
	
	#move to the relevant level
	def move_to_level_one(self) -> None:
		self.move_to_level(1)
	
	def move_to_level_two(self) -> None:
		self.move_to_level(2)
	
	def move_to_level_three(self) -> None:
		self.move_to_level(3)
	
	def move_to_level_four(self) -> None:
		self.move_to_level(4)
	
	def move_to_level_five(self) -> None:
		self.move_to_level(5)
	
	def move_to_final_boss(self) -> None:
		self.move_to_level(6)
	
	def move_to_create_account(self):
		"""
			Moves to the screen for the user to create an account

			Inputs:
				- None
			Outputs:
				- None

		"""
		# sets the background to white at the start of the program
		self.WIN.fill(self._main.colour_dict["Background"])
		
		#makes sure none of the boxes are focused when moving screens
		self.unfocus_boxes()
		
		# defines and draws an exit button to be used to close the game
		self.button_dict[("exit_button", "create_account")]: Button = (self.create_object(Button,
																						  (self.WIDTH - (5 * self.POINT_SIZE) - self.POINT_SIZE, self.POINT_SIZE),
																						  self.WIN, self.POINT_SIZE, (5 * self.POINT_SIZE), (5 * self.POINT_SIZE), self._main.colour_dict["No"], "exit_button"),
																	   self.close_game)
		# defines and creates a back button
		self.button_dict[("back_button", "create_account")]: Button = (self.create_object(Button,
																						  (self.POINT_SIZE, self.POINT_SIZE),
																						  self.WIN, self.POINT_SIZE, (5 * self.POINT_SIZE), (5 * self.POINT_SIZE), self._main.colour_dict["Back"], "back_button"),
																	   self.move_to_login)
		self.button_dict[("back_button", "create_account")][0].set_text("<-", self.FONT, self._main.colour_dict["Text"])
		
		# defines and draws an exit button to be used to close the game
		self.button_dict[("create_account", "create_account")]: Button = (self.create_object(Button,
																							 (80 * self.POINT_SIZE, 85 * self.POINT_SIZE),
																							 self.WIN, self.POINT_SIZE, (40 * self.POINT_SIZE), (10 * self.POINT_SIZE), self._main.colour_dict["Yes"], "create_account"),
																		  self._main.create_account)
		self.button_dict[("create_account", "create_account")][0].set_text("Create Account", self.FONT, self._main.colour_dict["Text"])
		
		#defines and draws boxes for the user to enter a username and password, as well as to confirm their password
		self.text_box_dict[("username", "create_account")] = self.create_object(TextInputBox,
																				(70 * self.POINT_SIZE, 30 * self.POINT_SIZE),
																				self.WIN, (60 * self.POINT_SIZE), (10 * self.POINT_SIZE), self.POINT_SIZE, self._main.colour_dict["Border"], 3, "username", self._main.colour_dict["Background"])
		self.text_box_dict[("password", "create_account")] = self.create_object(TextInputBox,
																				(70 * self.POINT_SIZE, 45 * self.POINT_SIZE),
																				self.WIN, (60 * self.POINT_SIZE), (10 * self.POINT_SIZE), self.POINT_SIZE, self._main.colour_dict["Border"], 3, "password", self._main.colour_dict["Background"])
		self.text_box_dict[("confirm_password", "create_account")] = self.create_object(TextInputBox,
																						(70 * self.POINT_SIZE, 60 * self.POINT_SIZE),
																						self.WIN, (60 * self.POINT_SIZE), (10 * self.POINT_SIZE), self.POINT_SIZE, self._main.colour_dict["Border"], 3, "confirm_password", self._main.colour_dict["Background"])
		#initializes the error text box
		self.box_dict[("info", "create_account")] = self.create_object(BoundingBox,
																	   (70 * self.POINT_SIZE, 20 * self.POINT_SIZE),
																	   self.WIN, (60 * self.POINT_SIZE), (10 * self.POINT_SIZE), self.POINT_SIZE, self._main.colour_dict["Background"], 4, self._main.colour_dict["Background"])
		self.box_dict[("info", "create_account")].set_text("", font.Font(resource_path("MainPrograms/Fonts/Roboto/static/Roboto-Bold.ttf"), int(self.POINT_SIZE * 3)), colour=self._main.colour_dict["Background"])
		
		#defines the type of the text box key
		key: tuple[str, str]
		
		# draw all the text_boxes
		for key in self.text_box_dict.keys():
			if key[1] != "create_account":
				continue
			
			# set the target text box
			target_text_box = self.text_box_dict[key]
			
			# draw it
			target_text_box.draw()
			
			# set the text depending on the character count
			if len(target_text_box.get_text()) == 0:
				key_name: str = key[0].replace("_", " ").capitalize()
				target_text_box.set_text(key_name, self.TEXTBOX_FONT, self._main.colour_dict["Text"])
			else:
				target_text_box.display_text(pygame.font.Font(resource_path("MainPrograms/Fonts/Roboto/static/Roboto-Bold.ttf"), int(self.POINT_SIZE * min(6.0, 7 - math.log2(max(1.0, 0.75 * len(target_text_box.get_text())))))), self._main.colour_dict["Text"])
		
		# set the screen type
		self._main.screen = "create_account"
	
	def move_to_login(self):
		"""
			Moves to the screen for the user to login

			Inputs:
				- None
			Outputs:
				- None

		"""
		# sets the background to white at the start of the program
		self.WIN.fill(self._main.colour_dict["Background"])
		
		#clears the focused attribute of text boxes
		self.unfocus_boxes()
		
		# defines and draws an exit button to be used to close the game
		self.button_dict[("exit_button", "login")]: Button = (self.create_object(Button,
																				 (self.WIDTH - (5 * self.POINT_SIZE) - self.POINT_SIZE, self.POINT_SIZE),
																				 self.WIN, self.POINT_SIZE, (5 * self.POINT_SIZE), (5 * self.POINT_SIZE), self._main.colour_dict["No"], "exit_button"),
															  self.close_game)
		# defines and creates a back button
		self.button_dict[("back_button", "login")]: Button = (self.create_object(Button,
																				 (self.POINT_SIZE, self.POINT_SIZE),
																				 self.WIN, self.POINT_SIZE, (5 * self.POINT_SIZE), (5 * self.POINT_SIZE), self._main.colour_dict["Back"], "back_button"),
															  self.move_to_home_screen)
		self.button_dict[("back_button", "login")][0].set_text("<-", self.FONT, self._main.colour_dict["Text"])
		
		# defines and draws an exit button to be used to close the game
		self.button_dict[("log_in", "login")]: Button = (self.create_object(Button,
																			(80 * self.POINT_SIZE, 70 * self.POINT_SIZE),
																			self.WIN, self.POINT_SIZE, (40 * self.POINT_SIZE), (10 * self.POINT_SIZE), self._main.colour_dict["Yes"], "log_in"),
														 self._main.validate_user)
		self.button_dict[("log_in", "login")][0].set_text("Log In", self.FONT, self._main.colour_dict["Text"])
		
		# defines and draws an exit button to be used to close the game
		self.button_dict[("create_account", "login")]: Button = (self.create_object(Button,
																					(80 * self.POINT_SIZE, 85 * self.POINT_SIZE),
																					self.WIN, self.POINT_SIZE, (40 * self.POINT_SIZE), (10 * self.POINT_SIZE), self._main.colour_dict["Yes"], "create_account"),
																 self.move_to_create_account)
		self.button_dict[("create_account", "login")][0].set_text("Create Account", self.FONT, self._main.colour_dict["Text"])
		
		# defines and draws a box for the user to enter their username
		self.text_box_dict[("username", "login")] = self.create_object(TextInputBox,
																	   (70 * self.POINT_SIZE, 30 * self.POINT_SIZE),
																	   self.WIN, (60 * self.POINT_SIZE), (10 * self.POINT_SIZE), self.POINT_SIZE, self._main.colour_dict["Border"], 3, "username", self._main.colour_dict["Background"])
		self.text_box_dict[("password", "login")] = self.create_object(TextInputBox,
																	   (70 * self.POINT_SIZE, 45 * self.POINT_SIZE),
																	   self.WIN, (60 * self.POINT_SIZE), (10 * self.POINT_SIZE), self.POINT_SIZE, self._main.colour_dict["Border"], 3, "password", self._main.colour_dict["Background"])
		
		# initializes the error text box
		self.box_dict[("info", "login")] = self.create_object(BoundingBox,
															  (70 * self.POINT_SIZE, 20 * self.POINT_SIZE),
															  self.WIN, (60 * self.POINT_SIZE), (10 * self.POINT_SIZE), self.POINT_SIZE, self._main.colour_dict["Background"], 4, self._main.colour_dict["Background"])
		self.box_dict[("info", "login")].set_text("", font.Font(resource_path("MainPrograms/Fonts/Roboto/static/Roboto-Bold.ttf"), int(self.POINT_SIZE * 3)), colour=self._main.colour_dict["Text"])
		
		# draw all the text_boxes
		for key in self.text_box_dict.keys():
			if key[1] != "login":
				continue
			
			#set the target text box
			target_text_box = self.text_box_dict[key]
			
			#draw it
			target_text_box.draw()
			
			#set the text depending on the character count
			if len(target_text_box.get_text()) == 0:
				key_name: str = key[0].replace("_", " ").capitalize()
				target_text_box.set_text(key_name, self.TEXTBOX_FONT, self._main.colour_dict["Text"])
			else:
				match target_text_box.get_name().lower():
					case "username":
						# update and display its text
						target_text_box.display_text(pygame.font.Font(resource_path("MainPrograms/Fonts/Roboto/static/Roboto-Bold.ttf"), int(self.POINT_SIZE * min(6.0, 7 - math.log2(max(1.0, 0.75 * len(target_text_box.get_text())))))), self._main.colour_dict["Text"])
					case "password":
						# update and display its text
						target_text_box.display_given_text("*" * len(target_text_box.get_text()), pygame.font.Font(resource_path("MainPrograms/Fonts/mine-sweeper.ttf"), int(self.POINT_SIZE * min(6.0, 7 - math.log2(max(1.0, 1.5 * len(target_text_box.get_text())))))), self._main.colour_dict["Text"])
		
		# set the screen type
		self._main.screen = "login"
	
	def move_to_options(self) -> None:
		"""
			Moves to the screen for the user to edit their options

			Inputs:
				- None
			Outputs:
				- None
		"""
		# sets the background to white at the start of the program
		self.WIN.fill(self._main.colour_dict["Background"])
		
		#clears the focused attribute on the text boxes
		self.unfocus_boxes()
		
		#sets the ready attribute to false
		# prevents the user from immediately clicking upon entering the options menu
		self._main._ready = False
		
		# defines and draws an exit button to be used to close the game
		self.button_dict[("exit_button", "options")]: Button = (self.create_object(Button,
																				   (self.WIDTH - (5 * self.POINT_SIZE) - self.POINT_SIZE, self.POINT_SIZE),
																				   self.WIN, self.POINT_SIZE, (5 * self.POINT_SIZE), (5 * self.POINT_SIZE), self._main.colour_dict["No"], "exit_button"),
																self.close_game)
		# defines and creates a back button
		self.button_dict[("back_button", "options")]: Button = (self.create_object(Button,
																				   (self.POINT_SIZE, self.POINT_SIZE),
																				   self.WIN, self.POINT_SIZE, (5 * self.POINT_SIZE), (5 * self.POINT_SIZE), self._main.colour_dict["Back"], "back_button"),
																self.move_to_home_screen)
		self.button_dict[("back_button", "options")][0].set_text("<-", self.FONT, self._main.colour_dict["Text"])
		
		#create and display the name for the dig text box
		self.box_dict[("dig_name", "options")] = self.create_object(BoundingBox,
																	(105 * self.POINT_SIZE, 20 * self.POINT_SIZE),
																	self.WIN, (10 * self.POINT_SIZE), (10 * self.POINT_SIZE), self.POINT_SIZE, self._main.colour_dict["Background"], 4, self._main.colour_dict["Background"])
		self.box_dict[("dig_name", "options")].set_text_left_just("Dig:", font.Font(resource_path("MainPrograms/Fonts/Roboto/static/Roboto-Bold.ttf"), int(self.POINT_SIZE * 5)), colour=self._main.colour_dict["Text"], offset=self.POINT_SIZE)
		
		# create and display the name for the flag text box
		self.box_dict[("flag_name", "options")] = self.create_object(BoundingBox,
																	 (25 * self.POINT_SIZE, 20 * self.POINT_SIZE),
																	 self.WIN, (10 * self.POINT_SIZE), (10 * self.POINT_SIZE), self.POINT_SIZE, self._main.colour_dict["Background"], 4, self._main.colour_dict["Background"])
		self.box_dict[("flag_name", "options")].set_text_left_just("Flag:", font.Font(resource_path("MainPrograms/Fonts/Roboto/static/Roboto-Bold.ttf"), int(self.POINT_SIZE * 5)), colour=self._main.colour_dict["Text"], offset=self.POINT_SIZE)
		
		# create and display the name for the chording toggle box
		self.box_dict[("chording_name", "options")] = self.create_object(BoundingBox,
																		 (25 * self.POINT_SIZE, 50 * self.POINT_SIZE),
																		 self.WIN, (10 * self.POINT_SIZE), (10 * self.POINT_SIZE), self.POINT_SIZE, self._main.colour_dict["Background"], 4, self._main.colour_dict["Background"])
		self.box_dict[("chording_name", "options")].set_text_left_just("Chording:", font.Font(resource_path("MainPrograms/Fonts/Roboto/static/Roboto-Bold.ttf"), int(self.POINT_SIZE * 5)), colour=self._main.colour_dict["Text"], offset=self.POINT_SIZE)
		
		# create and display the name for the theme dropdown menu
		self.box_dict[("theme_name", "options")] = self.create_object(BoundingBox,
																	  (105 * self.POINT_SIZE, 50 * self.POINT_SIZE),
																	  self.WIN, (10 * self.POINT_SIZE), (10 * self.POINT_SIZE), self.POINT_SIZE, self._main.colour_dict["Background"], 4, self._main.colour_dict["Background"])
		self.box_dict[("theme_name", "options")].set_text_left_just("Theme:", font.Font(resource_path("MainPrograms/Fonts/Roboto/static/Roboto-Bold.ttf"), int(self.POINT_SIZE * 5)), colour=self._main.colour_dict["Text"], offset=self.POINT_SIZE)
		
		#create the objects for the keybinds. Does not overwrite them if they already exist to preserve their settings
		keybinds = self._main.keybind_dict
		self.keybind_dict[("dig", "options")] = self.create_object(KeybindBox,
																   (130 * self.POINT_SIZE, 20 * self.POINT_SIZE),
																   self.WIN, (40 * self.POINT_SIZE), (10 * self.POINT_SIZE), self.POINT_SIZE, self._main.colour_dict["Border"], 4, "dig", self._main.colour_dict["Background"], keybinds["dig"])
		self.keybind_dict[("dig", "options")].set_key(keybinds["dig"])
		self.keybind_dict[("flag", "options")] = self.create_object(KeybindBox,
																	(40 * self.POINT_SIZE, 20 * self.POINT_SIZE),
																	self.WIN, (40 * self.POINT_SIZE), (10 * self.POINT_SIZE), self.POINT_SIZE, self._main.colour_dict["Border"], 4, "flag", self._main.colour_dict["Background"], keybinds["flag"])
		self.keybind_dict[("flag", "options")].set_key(keybinds["flag"])
		self.toggle_box_dict[("chording", "options")] = self.create_object(ToggleBox,
																		   (70 * self.POINT_SIZE, 50 * self.POINT_SIZE),
																		   self.WIN, (10 * self.POINT_SIZE), (10 * self.POINT_SIZE), self.POINT_SIZE, self._main.colour_dict["Border"], 4, "chording", self._main.colour_dict["Yes"], self._main.colour_dict["No"])
		
		#if chording is off but the chording toggle box is on, toggle off the toggle box
		if not self._main.chording and self.toggle_box_dict[("chording", "options")].get_active():
			self.toggle_box_dict[("chording", "options")].on_click()
		
		#get the options from the database
		options = self._main.validator.get_options()
		
		#write the name of the slider onto the screen
		self.box_dict[("music_name", "login")] = self.create_object(BoundingBox,
																	(25 * self.POINT_SIZE, 77.5 * self.POINT_SIZE),
																	self.WIN, (10 * self.POINT_SIZE), (10 * self.POINT_SIZE), self.POINT_SIZE, self._main.colour_dict["Background"], 4, self._main.colour_dict["Background"])
		self.box_dict[("music_name", "login")].set_text_left_just("Music volume:", font.Font(resource_path("MainPrograms/Fonts/Roboto/static/Roboto-Bold.ttf"), int(self.POINT_SIZE * 3)), colour=self._main.colour_dict["Text"], offset=self.POINT_SIZE)
		
		#define the slider and its orb
		self.slider_dict[("music_volume", "options")]: tuple[Slider, SliderOrb] = (self.create_object(Slider,
																									  (50 * self.POINT_SIZE, 80 * self.POINT_SIZE),
																									  self.WIN, (30 * self.POINT_SIZE), self.POINT_SIZE, self._main.colour_dict["Text"], 3),
																				   self.create_object(SliderOrb,
																									  (50 * self.POINT_SIZE, 80 * self.POINT_SIZE),
																									  self.WIN, (2.5 * self.POINT_SIZE), self.POINT_SIZE, self._main.colour_dict["Text"], 4, self._main.colour_dict["Background"]))
		slider, slider_orb = self.slider_dict[("music_volume", "options")]
		
		#move the slider based on the user's settings
		slider_orb.clear()
		slider.draw()
		slider_orb.move(slider_orb.get_pos()[0] + round((math.log2(self._main.music_volume * 31 + 1)) * slider.get_length() / 5, 3))
		
		# write the name of the slider onto the screen
		self.box_dict[("sfx_name", "login")] = self.create_object(BoundingBox,
																  (105 * self.POINT_SIZE, 77.5 * self.POINT_SIZE),
																  self.WIN, (10 * self.POINT_SIZE), (10 * self.POINT_SIZE), self.POINT_SIZE, self._main.colour_dict["Background"], 4, self._main.colour_dict["Background"])
		self.box_dict[("sfx_name", "login")].set_text_left_just("SFX volume:", font.Font(resource_path("MainPrograms/Fonts/Roboto/static/Roboto-Bold.ttf"), int(self.POINT_SIZE * 3)), colour=self._main.colour_dict["Text"], offset=self.POINT_SIZE)
		
		# define the slider and its orb
		self.slider_dict[("sfx_volume", "options")]: tuple[Slider, SliderOrb] = (self.create_object(Slider,
																									(140 * self.POINT_SIZE, 80 * self.POINT_SIZE),
																									self.WIN, (30 * self.POINT_SIZE), self.POINT_SIZE, self._main.colour_dict["Text"], 3),
																				 self.create_object(SliderOrb,
																									(140 * self.POINT_SIZE, 80 * self.POINT_SIZE),
																									self.WIN, (2.5 * self.POINT_SIZE), self.POINT_SIZE, self._main.colour_dict["Text"], 4, self._main.colour_dict["Background"]))
		slider, slider_orb = self.slider_dict[("sfx_volume", "options")]
		
		# move the slider based on the user's settings
		slider_orb.clear()
		slider.draw()
		slider_orb.move(slider_orb.get_pos()[0] + round((math.log2(self._main.sfx_volume * 31 + 1)) * slider.get_length() / 5, 3))
		
		#All the theme options
		themes = ["Standard", "Dark", "Green", "Blue", "Pink"]
		
		#create a dropdown menu
		self.dropdown_dict[("theme", "options")] = (self.create_object(DropdownBox,
																	   (130 * self.POINT_SIZE, 50 * self.POINT_SIZE),
																	   self.WIN, (40 * self.POINT_SIZE), (10 * self.POINT_SIZE), self.POINT_SIZE, self._main.colour_dict["Border"], 3, "theme", self._main.colour_dict["Background"]),
													*(DropdownOption(self.WIN, (40 * self.POINT_SIZE), (7 * self.POINT_SIZE), self.POINT_SIZE, self._main.colour_dict["Border"], 1, name, self._main.colour_dict["Background"]) for name in themes))
		
		#if logged in
		if self._main.validator.get_user_logged_in():
			#get the theme name from the database
			self._main.theme = self._main.validator.get_options()["theme"]
			self.dropdown_dict[("theme", "options")][0].set_current_option(self._main.theme)
		
		else:
			#use the default
			self.dropdown_dict[("theme", "options")][0].set_current_option(self._main.theme)
		
		#get the text from the dropdown box
		text = self.dropdown_dict[("theme", "options")][0].get_current_option().capitalize()
		
		#set the dropdown text
		self.dropdown_dict[("theme", "options")][0].set_text(text, font.Font(resource_path("MainPrograms/Fonts/Roboto/static/Roboto-Bold.ttf"), int(self.POINT_SIZE * 5.5)), self._main.colour_dict["Text"])
		
		# draw all the keybind boxes
		for keybind_key in self.keybind_dict.keys():
			if keybind_key[1] != "options":
				continue
			
			# draw
			self.keybind_dict[keybind_key].draw()
			
			# display the name according to the length of its text
			key_text = self.keybind_dict[keybind_key].get_text()
			self.keybind_dict[keybind_key].display_text(key_text, pygame.font.Font(resource_path("MainPrograms/Fonts/Roboto/static/Roboto-Bold.ttf"), int(self.POINT_SIZE * min(6.0, 7 - math.log2(max(1.0, 0.75 * len(self.keybind_dict[keybind_key].get_text())))))), self._main.colour_dict["Text"])
		
		# draw all the toggle boxes
		for toggle_key in self.toggle_box_dict.keys():
			if toggle_key[1] != "options":
				continue
			
			#store the toggle_box item
			toggle_box = self.toggle_box_dict[toggle_key]
			
			#draw it with its primary colour
			toggle_box.initial_draw(options[toggle_box.get_name()])
		
		# set the screen type
		self._main.screen = "options"
	
	def move_sliders(self, mouse_pos: Coordinate, screen: str) -> None:
		"""
			Moves the sliders based on the user's mouse inputs
			
			Inputs:
				- mouse_pos: the user's mouse position on screen
				- screen: the current screen
			OutputsL
				- None
		
		"""
		#for every slider
		for slider_name in self.slider_dict.keys():
			
			#skip sliders not on this screen
			if slider_name[1] != screen:
				continue
			
			#initialize types
			slider: Slider
			slider_orb: SliderOrb
			
			#store the slider and slider orb
			slider, slider_orb = self.slider_dict[slider_name]
			
			#if the mouse is on the orb, and the mouse has been pressed
			if slider_orb.check_clicked(mouse_pos) and pygame.mouse.get_pressed()[0]:
				# get the mouse movement since the last call
				new_position_x = mouse_pos[0]
				
				#prevent the orb from moving off the slider
				if new_position_x - slider.get_pos()[0] < 0:
					new_position_x = slider.get_pos()[0]
				elif new_position_x - slider.get_pos()[0] > slider.get_length():
					new_position_x = slider.get_pos()[0] + slider.get_length()
				
				#redraw the slider
				slider_orb.clear()
				slider.draw()
				slider_orb.move(new_position_x)
				
				#set the music volume
				if "music" in slider_name[0]:
					#calculate the new volume for the music
					self._main.music_volume = round((2 ** (0.05 * slider.get_percent(new_position_x)) - 1) / (2 ** 5 - 1), 3)
					
					#set the volume
					pygame.mixer.music.set_volume(self._main.music_volume)
					self._main.validator.set_option(self._main.music_volume, "music")
				
				#set the sfx volume for every channel
				elif "sfx" in slider_name[0]:
					# calculate the new volume for the music
					self._main.sfx_volume = round((2 ** (0.05 * slider.get_percent(new_position_x)) - 1) / (2 ** 5 - 1), 3)
					
					# set the volume in all channels
					for i in range(16):
						pygame.mixer.Channel(i).set_volume(self._main.sfx_volume)
					self._main.validator.set_option(self._main.sfx_volume, "sfx")
	
	@staticmethod
	def get_colour_dict(name: str) -> dict[str: Colour]:
		"""
			Returns a dictionary of colours based on the input theme
			
			Inputs:
				- name: the name of the theme
			Outputs:
				- dict: the dictionary of colours
		 
		"""
		if name == "Standard":
			return {
				"Background": (255, 255, 255),
				"Border": (0, 0, 0),
				"Yes": (0, 255, 0),
				"No": (255, 0, 0),
				"Back": (0, 0, 255),
				"Space": (153, 246, 255),
				"Text": (0, 0, 0),
				"Tile start": (0, 0, 0),
				"Tile end": (160, 32, 160),
				"Tile back": (230, 245, 255),
				"Flag back": (200, 210, 230)
			}
		elif name == "Dark":
			return {
				"Background": (30, 30, 30),
				"Border": (255, 255, 255),
				"Yes": (0, 150, 0),
				"No": (150, 0, 0),
				"Back": (0, 0, 150),
				"Space": (153, 246, 255),
				"Text": (255, 255, 255),
				"Tile start": (255, 255, 255),
				"Tile end": (160, 32, 160),
				"Tile back": (50, 50, 50),
				"Flag back": (100, 100, 100)
			}
		elif name == "Green":
			return {
				"Background": (200, 255, 200),
				"Border": (0, 0, 0),
				"Yes": (0, 150, 0),
				"No": (255, 0, 0),
				"Back": (0, 0, 255),
				"Space": (153, 246, 255),
				"Text": (0, 0, 0),
				"Tile start": (0, 0, 0),
				"Tile end": (32, 160, 32),
				"Tile back": (175, 255, 175),
				"Flag back": (100, 200, 100)
			}
		elif name == "Blue":
			return {
				"Background": (175, 200, 255),
				"Border": (0, 0, 0),
				"Yes": (0, 200, 0),
				"No": (255, 0, 0),
				"Back": (0, 0, 255),
				"Space": (153, 246, 255),
				"Text": (0, 0, 0),
				"Tile start": (0, 0, 0),
				"Tile end": (32, 32, 160),
				"Tile back": (175, 175, 255),
				"Flag back": (100, 100, 200)
			}
		elif name == "Pink":
			return {
				"Background": (255, 210, 210),
				"Border": (0, 0, 0),
				"Yes": (100, 255, 100),
				"No": (255, 50, 50),
				"Back": (100, 100, 255),
				"Space": (153, 246, 255),
				"Text": (0, 0, 0),
				"Tile start": (0, 0, 0),
				"Tile end": (255, 50, 50),
				"Tile back": (255, 175, 175),
				"Flag back": (200, 100, 100)
			}
		
		return None
	
	def options_left_click(self, mouse_pos) -> None:
		"""
			Code to execute when the user completes a left click on the options menu
			
			Inputs:
				- mouse_pos: the position of the mouse on the screen
			Outputs:
				- None
		"""
		# for each dropdown button
		for dropdown_key in self.dropdown_dict.keys():
			if dropdown_key[1] != "options":
				continue
			
			# get the button and its options
			dropdown_box, *dropdown_options = self.dropdown_dict[dropdown_key]
			
			# check if the dropdown box was clicked
			check_clicked = dropdown_box.check_drop_box_clicked(mouse_pos)
			
			# if it was clicked and is not already focused
			if check_clicked and not dropdown_box.get_focused():
				
				# it is now focused
				dropdown_box.set_focused(True)
				
				# for each of its options
				for i in range(len(dropdown_options)):
					# get its option
					dropdown_option: DropdownOption = dropdown_options[i]
					
					# display it
					dropdown_option.set_pos((130 * self.POINT_SIZE, 61 * self.POINT_SIZE + (8 * self.POINT_SIZE * i)))
					dropdown_option.set_visible(True)
					dropdown_option.update()
					
					# display the text
					dropdown_option.set_text(dropdown_option.get_name(), self.TEXTBOX_FONT_2, self._main.colour_dict["Text"])
				
				break
			
			# if it is clicked and is already focused
			elif check_clicked and dropdown_box.get_focused():
				
				# it is now not focused
				dropdown_box.set_focused(False)
				
				# set its gamemode to the default (its name)
				dropdown_box.set_current_option(dropdown_box.get_name().capitalize())
				
				# redraw the screen
				self.move_to_options()
			
			# for each dropdown option
			for i in range(len(dropdown_options)):
				dropdown_option: DropdownOption = dropdown_options[i]
				
				# if it is not visible, none of them are so skip
				if not dropdown_option.get_visible():
					break
				
				# check if it clicked
				dropdown_clicked = dropdown_option.check_drop_option_clicked(mouse_pos)
				
				# if it has been clicked
				if dropdown_clicked:
					# redraw the screen
					dropdown_box.update()
					dropdown_box.set_current_option(dropdown_option.get_name().capitalize())
					
					#set the colour dictionary to the new one for the theme
					self._main.colour_dict = self.get_colour_dict(dropdown_option.get_name().capitalize())
					self._main.theme = dropdown_option.get_name().capitalize()
					
					#if the user is logged in, save it to their settings in the database
					if self._main.validator.get_user_logged_in():
						self._main.validator.set_option(dropdown_option.get_name().capitalize(), "theme")
					
					#update the colour for all the objects
					#TextInputBox
					for text_box_key in self.text_box_dict.keys():
						self.text_box_dict[text_box_key].update_colour(background_colour=self._main.colour_dict["Background"], border_colour=self._main.colour_dict["Border"])
					
					# BoundingBox
					for bounding_box_key in self.box_dict.keys():
						self.box_dict[bounding_box_key].update_colour(background_colour=self._main.colour_dict["Background"], border_colour=self._main.colour_dict["Border"])
					
					#DropdownBox and DropdownOption
					for dropdown_box_key in self.dropdown_dict.keys():
						self.dropdown_dict[dropdown_box_key][0].update_colour(background_colour=self._main.colour_dict["Background"], border_colour=self._main.colour_dict["Border"])
						for j in range(1, len(self.dropdown_dict[dropdown_box_key])):
							self.dropdown_dict[dropdown_box_key][j].update_colour(background_colour=self._main.colour_dict["Background"], border_colour=self._main.colour_dict["Border"])
					
					#KeybindBox
					for keybind_box_key in self.keybind_dict.keys():
						self.keybind_dict[keybind_box_key].update_colour(background_colour=self._main.colour_dict["Background"], border_colour=self._main.colour_dict["Border"])
					
					#Tile
					for row in range(len(self.tile_board)):
						for col in range(len(self.tile_board[0])):
							self.tile_board[row][col].update_colour(background_colour=self._main.colour_dict["Background"], border_colour=self._main.colour_dict["Border"])
					
					#ToggleBox
					for toggle_key in self.toggle_box_dict.keys():
						self.toggle_box_dict[toggle_key].update_colour(primary_colour=self._main.colour_dict["Yes"], secondary_colour=self._main.colour_dict["No"], border_colour=self._main.colour_dict["Border"])
					
					# redraw the screen
					self.move_to_options()
					
					# it is now no longer focused
					dropdown_box.set_focused(False)
					
					break
	
	def on_win(self, public_board: Board, private_board: Board, minecount: int) -> int:
		"""
			Auto completes all flag upon the user winning
			
			Inputs:
				- public_board: the board available to the user
				- private_board: the board the user is completing
				- minecount: the current minecount
			Outputs:
				- minecount: the new minecount after this function finishes (should be 0)
		"""
		
		#for every item in the public board
		for row in range(len(public_board)):
			for col in range(len(public_board)):
				
				#if there are still covered mines
				if private_board[row][col] == -1 and public_board[row][col] == -2:
					#get the tile object
					tile_object = self.tile_board[row][col]
					
					#change the background to the flag background
					tile_object.update_colour(background_colour=self._main.colour_dict["Flag back"])
					
					# set the tile to a mine
					tile_object.update()
					tile_object.set_value(-4)
					tile_object.set_text("`", self.TILE_FONT)
					
					# redraw the board box
					self.box_dict[("board_box", "gameplay")].draw()
					
					# update and display the new minecount
					minecount -= 1
					self.box_dict[("minecount_box", "gameplay")].update()
					self.box_dict[("minecount_box", "gameplay")].set_text(str(minecount), self.FONT)
		
		return minecount
	
	def move_to_tutorial_screen(self) -> None:
		"""
			Move to the level select screen

			Inputs:
				- None
			Outputs:
				- None
		"""
		# clear the surface
		self.WIN.fill(self._main.colour_dict["Background"])
		
		#clear the focused attribute on all text boxes
		self.unfocus_boxes()
		
		#set the current screen to the tutorial select screen
		self._main.screen = "tutorial_select"
		
		# display the title
		text = self.create_object(BoundingBox,
								  (100 * self.POINT_SIZE, 10 * self.POINT_SIZE),
								  self.WIN, 0, 0, self.POINT_SIZE, self._main.colour_dict["Border"], 0, self._main.colour_dict["Background"])
		text.set_text("Tutorial", pygame.font.Font(resource_path("MainPrograms/Fonts/mine-sweeper.ttf"), int(self.POINT_SIZE * 6)), self._main.colour_dict["Text"])
		pygame.display.update()
		
		#defines and creates buttons to enter each tutorial level.
		#level 1
		self.button_dict[("level_one", "tutorial_select")] = (self.create_object(Button,
																				 (9 * self.POINT_SIZE, 20 * self.POINT_SIZE),
																				 self.WIN, self.POINT_SIZE, (30 * self.POINT_SIZE), (30 * self.POINT_SIZE), tuple([max(0, int((3 / 5) * self._main.colour_dict["Yes"][i])) for i in range(3)]), "level_one"),
															  self.move_to_tutorial_one)
		self.button_dict[("level_one", "tutorial_select")][0].set_text("Level 1", pygame.font.Font(resource_path("MainPrograms/Fonts/mine-sweeper.ttf"), int(self.POINT_SIZE * 3.5)), self._main.colour_dict["Text"])
		
		#level 2
		self.button_dict[("level_two", "tutorial_select")] = (self.create_object(Button,
																				 (47 * self.POINT_SIZE, 20 * self.POINT_SIZE),
																				 self.WIN, self.POINT_SIZE, (30 * self.POINT_SIZE), (30 * self.POINT_SIZE), tuple([max(0, int((7 / 10) * self._main.colour_dict["Yes"][i])) for i in range(3)]), "level_two"),
															  self.move_to_tutorial_two)
		self.button_dict[("level_two", "tutorial_select")][0].set_text("Level 2", pygame.font.Font(resource_path("MainPrograms/Fonts/mine-sweeper.ttf"), int(self.POINT_SIZE * 3.5)), self._main.colour_dict["Text"])
		
		# level 3
		self.button_dict[("level_three", "tutorial_select")] = (self.create_object(Button,
																				   (85 * self.POINT_SIZE, 20 * self.POINT_SIZE),
																				   self.WIN, self.POINT_SIZE, (30 * self.POINT_SIZE), (30 * self.POINT_SIZE), tuple([max(0, int((4 / 5) * self._main.colour_dict["Yes"][i])) for i in range(3)]), "level_three"),
																self.move_to_tutorial_three)
		self.button_dict[("level_three", "tutorial_select")][0].set_text("Level 3", pygame.font.Font(resource_path("MainPrograms/Fonts/mine-sweeper.ttf"), int(self.POINT_SIZE * 3.5)), self._main.colour_dict["Text"])
		
		# level 4
		self.button_dict[("level_four", "tutorial_select")] = (self.create_object(Button,
																				  (123 * self.POINT_SIZE, 20 * self.POINT_SIZE),
																				  self.WIN, self.POINT_SIZE, (30 * self.POINT_SIZE), (30 * self.POINT_SIZE), tuple([max(0, int((9 / 10) * self._main.colour_dict["Yes"][i])) for i in range(3)]), "level_four"),
															   self.move_to_tutorial_four)
		self.button_dict[("level_four", "tutorial_select")][0].set_text("Level 4", pygame.font.Font(resource_path("MainPrograms/Fonts/mine-sweeper.ttf"), int(self.POINT_SIZE * 3.5)), self._main.colour_dict["Text"])
		
		# level 5
		self.button_dict[("level_five", "tutorial_select")] = (self.create_object(Button,
																				  (161 * self.POINT_SIZE, 20 * self.POINT_SIZE),
																				  self.WIN, self.POINT_SIZE, (30 * self.POINT_SIZE), (30 * self.POINT_SIZE), self._main.colour_dict["Yes"], "level_five"),
															   self.move_to_tutorial_five)
		self.button_dict[("level_five", "tutorial_select")][0].set_text("Level 5", pygame.font.Font(resource_path("MainPrograms/Fonts/mine-sweeper.ttf"), int(self.POINT_SIZE * 3.5)), self._main.colour_dict["Text"])
		
		#level 6
		self.button_dict[("level_six", "tutorial_select")] = (self.create_object(Button,
																				 (9 * self.POINT_SIZE, 60 * self.POINT_SIZE),
																				 self.WIN, self.POINT_SIZE, (30 * self.POINT_SIZE), (30 * self.POINT_SIZE), tuple([max(0, int((3 / 5) * self._main.colour_dict["Yes"][i])) for i in range(3)]), "level_six"),
															  self.move_to_tutorial_six)
		self.button_dict[("level_six", "tutorial_select")][0].set_text("Level 6", pygame.font.Font(resource_path("MainPrograms/Fonts/mine-sweeper.ttf"), int(self.POINT_SIZE * 3.5)), self._main.colour_dict["Text"])
		
		# level 7
		self.button_dict[("level_seven", "tutorial_select")] = (self.create_object(Button,
																				   (47 * self.POINT_SIZE, 60 * self.POINT_SIZE),
																				   self.WIN, self.POINT_SIZE, (30 * self.POINT_SIZE), (30 * self.POINT_SIZE), tuple([max(0, int((7 / 10) * self._main.colour_dict["Yes"][i])) for i in range(3)]), "level_seven"),
																self.move_to_tutorial_seven)
		self.button_dict[("level_seven", "tutorial_select")][0].set_text("Level 7", pygame.font.Font(resource_path("MainPrograms/Fonts/mine-sweeper.ttf"), int(self.POINT_SIZE * 3.5)), self._main.colour_dict["Text"])
		
		# level 8
		self.button_dict[("level_eight", "tutorial_select")] = (self.create_object(Button,
																				   (85 * self.POINT_SIZE, 60 * self.POINT_SIZE),
																				   self.WIN, self.POINT_SIZE, (30 * self.POINT_SIZE), (30 * self.POINT_SIZE), tuple([max(0, int((4 / 5) * self._main.colour_dict["Yes"][i])) for i in range(3)]), "level_eight"),
																self.move_to_tutorial_eight)
		self.button_dict[("level_eight", "tutorial_select")][0].set_text("Level 8", pygame.font.Font(resource_path("MainPrograms/Fonts/mine-sweeper.ttf"), int(self.POINT_SIZE * 3.5)), self._main.colour_dict["Text"])
		
		# level 9
		self.button_dict[("level_nine", "tutorial_select")] = (self.create_object(Button,
																				  (123 * self.POINT_SIZE, 60 * self.POINT_SIZE),
																				  self.WIN, self.POINT_SIZE, (30 * self.POINT_SIZE), (30 * self.POINT_SIZE), tuple([max(0, int((9 / 10) * self._main.colour_dict["Yes"][i])) for i in range(3)]), "level_nine"),
															   self.move_to_tutorial_nine)
		self.button_dict[("level_nine", "tutorial_select")][0].set_text("Level 9", pygame.font.Font(resource_path("MainPrograms/Fonts/mine-sweeper.ttf"), int(self.POINT_SIZE * 3.5)), self._main.colour_dict["Text"])
		
		#final boss
		self.button_dict[("final_boss", "tutorial_select")] = (self.create_object(Button,
																				  (161 * self.POINT_SIZE, 60 * self.POINT_SIZE),
																				  self.WIN, self.POINT_SIZE, (30 * self.POINT_SIZE), (30 * self.POINT_SIZE), self._main.colour_dict["Yes"], "final_boss"),
															   self.move_to_tutorial_final_boss)
		self.button_dict[("final_boss", "tutorial_select")][0].set_text("Level 10", pygame.font.Font(resource_path("MainPrograms/Fonts/mine-sweeper.ttf"), int(self.POINT_SIZE * 3.5)), self._main.colour_dict["Text"])
		
		# defines and creates a start button
		self.button_dict[("exit_button", "tutorial_select")]: Button = (self.create_object(Button,
																						   (self.WIDTH - (5 * self.POINT_SIZE) - self.POINT_SIZE, self.POINT_SIZE),
																						   self.WIN, self.POINT_SIZE, (5 * self.POINT_SIZE), (5 * self.POINT_SIZE), self._main.colour_dict["No"], "exit_button"),
																		self.close_game)
		# defines and creates a back button
		self.button_dict[("back_button", "tutorial_select")]: Button = (self.create_object(Button,
																						   (self.POINT_SIZE, self.POINT_SIZE),
																						   self.WIN, self.POINT_SIZE, (5 * self.POINT_SIZE), (5 * self.POINT_SIZE), self._main.colour_dict["Back"], "back_button"),
																		self.move_to_gameplay_options_screen)
		self.button_dict[("back_button", "tutorial_select")][0].set_text("<-", self.FONT, self._main.colour_dict["Text"])
	
	#move to the relevant tutorial level
	def move_to_tutorial_one(self) -> None:
		self.move_to_tutorial(1)
	
	def move_to_tutorial_two(self) -> None:
		self.move_to_tutorial(2)
	
	def move_to_tutorial_three(self) -> None:
		self.move_to_tutorial(3)
	
	def move_to_tutorial_four(self) -> None:
		self.move_to_tutorial(4)
	
	def move_to_tutorial_five(self) -> None:
		self.move_to_tutorial(5)
	
	def move_to_tutorial_six(self) -> None:
		self.move_to_tutorial(6)
	
	def move_to_tutorial_seven(self) -> None:
		self.move_to_tutorial(7)
	
	def move_to_tutorial_eight(self) -> None:
		self.move_to_tutorial(8)
	
	def move_to_tutorial_nine(self) -> None:
		self.move_to_tutorial(9)
	
	def move_to_tutorial_final_boss(self) -> None:
		self.move_to_level(10)
	
	def move_to_tutorial(self, tutorial_level: int) -> None:
		"""
			Moves to the tutorial screen

			Inputs:
				- tutorial_level: the level for the tutorial
			Outputs:
				None

		"""
		# sets the background to white at the start of the program
		self.WIN.fill(self._main.colour_dict["Background"])
		
		#clears the focused attribute on all text boxes
		self.unfocus_boxes()
		
		# defines and draws an exit button to be used to close the game
		self.button_dict[("exit_button", "tutorial")]: Button = (self.create_object(Button,
																					(self.WIDTH - (5 * self.POINT_SIZE) - self.POINT_SIZE, self.POINT_SIZE),
																					self.WIN, self.POINT_SIZE, (5 * self.POINT_SIZE), (5 * self.POINT_SIZE), self._main.colour_dict["No"], "exit_button"),
																 self.close_game)
		# defines and creates a back button
		self.button_dict[("back_button", "tutorial")]: Button = (self.create_object(Button,
																					(self.POINT_SIZE, self.POINT_SIZE),
																					self.WIN, self.POINT_SIZE, (5 * self.POINT_SIZE), (5 * self.POINT_SIZE), self._main.colour_dict["Back"], "back_button"),
																 self.move_to_tutorial_screen)
		self.button_dict[("back_button", "tutorial")][0].set_text("<-", self.FONT, self._main.colour_dict["Text"])
		
		# initializes the sublevel
		sublevel_count_list: list[int] = [3, 2, 1, 1, 2, 3, 1, 1, 1, 1]
		
		for i in range(1, sublevel_count_list[tutorial_level - 1]):
			# defines and creates a divider line
			self.create_object(BoundingBox,
							   (i * self.WIDTH / sublevel_count_list[tutorial_level - 1], 0),
							   self.WIN, 4, self.HEIGHT, self.POINT_SIZE, self._main.colour_dict["Text"], 4, self._main.colour_dict["Text"])
		
		#for each board in this tutorial level
		for sublevel in range(1, sublevel_count_list[tutorial_level - 1] + 1):
			
			#gets the private and public board, as well as the path to the description png from the database
			private_board, public_board, description_path = self._main.level_manager.get_tutorial(tutorial_level, sublevel)
			
			#initialize the boards in the dict - (tile board, private board, public board)
			self.tutorial_board_dict[(tutorial_level, sublevel)]: tuple[list[list[Tile]], Board, Board] = ([], [], [])
			
			#for level 6.2, the bounding box should be invisible, as it is a diagram, not text
			if tutorial_level == 6 and sublevel == 2:
				describer_box = self.create_object(BoundingBox,
												   ((-1 + 2 * sublevel) * self.WIDTH / (2 * sublevel_count_list[tutorial_level - 1]) - 30 * self.POINT_SIZE, 10 * self.POINT_SIZE),
												   self.WIN, 60 * self.POINT_SIZE, 40 * self.POINT_SIZE, self.POINT_SIZE, self._main.colour_dict["Background"], 4, self._main.colour_dict["Background"])
			else:
				describer_box = self.create_object(BoundingBox,
												   ((-1 + 2 * sublevel) * self.WIDTH / (2 * sublevel_count_list[tutorial_level - 1]) - 30 * self.POINT_SIZE, 10 * self.POINT_SIZE),
												   self.WIN, 60 * self.POINT_SIZE, 40 * self.POINT_SIZE, self.POINT_SIZE, self._main.colour_dict["Text"], 4, self._main.colour_dict["Background"])
			describer_box.set_image(str(resource_path(description_path)))
			
			# initialize the tile board
			#for each row
			for rows in range(len(private_board)):
				#initialize a list to stall all the tiles this row
				row: list[Tile] = []
				
				#for each column
				for cols in range(len(private_board[0])):
					#initialize, position and display a tile 
					tile = Tile(
						surface=self.WIN,
						tile_size=10 * self.POINT_SIZE,
						point_size=self.POINT_SIZE,
						border_colour=self._main.colour_dict["Border"],
						border_width=1,
						tile_coordinate=(rows, cols),
						rows=len(private_board),
						cols=len(private_board[0]),
						text_colour_start=self._main.colour_dict["Tile start"],
						text_colour_end=self._main.colour_dict["Tile end"],
						background_colour=self._main.colour_dict["Background"]
					)
					
					position: Coordinate = (
						(-1 + 2 * sublevel) * self.WIDTH / (2 * sublevel_count_list[tutorial_level - 1]) - 5 * self.POINT_SIZE * len(private_board[0]) + 10 * self.POINT_SIZE * cols,
						self.HEIGHT / 2 + 10 * self.POINT_SIZE * rows
					)
					
					#center the board in the sublevel
					tile.set_pos(position)
					
					#set the balue the user sees
					tile.set_value(public_board[rows][cols])
					tile.draw()
					
					#add the tile to the row
					row.append(tile)
				#add the row to the tile board
				self.tutorial_board_dict[(tutorial_level, sublevel)][0].append(row)
			
			#update the dictionary
			self.tutorial_board_dict[(tutorial_level, sublevel)] = self.tutorial_board_dict[(tutorial_level, sublevel)][0], private_board, public_board
			
			# update the public board with the revealed tiles
			for row in range(len(public_board)):
				for col in range(len(public_board[0])):
					#if space
					if public_board[row][col] == -3:
						# set its colour to the space colour
						self.tutorial_board_dict[(tutorial_level, sublevel)][0][row][col].fill(self._main.colour_dict["Space"])
					#if a number
					elif public_board[row][col] != -2:
						self.tutorial_board_dict[(tutorial_level, sublevel)][0][row][col].set_text(str(private_board[row][col]), self.TILE_FONT)
						self.tutorial_board_dict[(tutorial_level, sublevel)][0][row][col].set_value(private_board[row][col])
		
		# set the screen type
		self._main.screen = "tutorial"
		
		#prevent clicking immediately upon screen change
		self._main._ready = False
		
		#indicate the current tutorial level
		self._main.current_level = tutorial_level
