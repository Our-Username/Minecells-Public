from pygame.font import Font
from MainPrograms.ObjectClasses.BoundingBox import BoundingBox
from MainPrograms.ObjectClasses.Tile import Tile
from MainPrograms.Queue import Queue
import pygame
import sys
import os
from pygame import Surface

POINT_SIZE: float = 1920 / 200

type Board = list[list[int]]
type TilePosition = tuple[int, int]
type Colour = tuple[int, int, int]


def resource_path(relative_path):
	if hasattr(sys, "_MEIPASS"):
		return os.path.join(sys._MEIPASS, relative_path)
	return os.path.join(os.path.abspath("."), relative_path)


def get_flags(position_clicked, directions, public_board, rows, cols) -> set[TilePosition]:
	"""
		Gets the positions of the flags adjacent to the given tile
		
		Inputs:
			- position_clicked: the position of the tile to check
			- directions: the positions of the tiles that this tile looks at
			- public_board: the board to check against
			- rows: the height of the public board
			- cols: the width of the public board
		Outputs:
			- output_set: the set of the positions of the flags
	"""
	
	output_set: set[TilePosition] = set()  # initialise output set
	
	for row, col in directions:  # for each adjacent tile
		rx, ry = position_clicked[0] + row, position_clicked[1] + col
		if 0 <= rx < rows and 0 <= ry < cols:  # if tile is within board
			if public_board[rx][ry] == -4:  # if tile is a flag
				output_set.add((rx, ry))
	return output_set


def _check_chording(position_clicked, directions, public_board) -> bool:
	"""
		Checks if the number of flags adjacent to the current tile equals (or exceeds) the number on the tile
		
		Inputs:
			- position_clicked: the position of the tile to check
			- directions: the positions of the tiles that this tile looks at
			- public_board: the board to check against
		Outputs:
			- bool: whether chording is available here
	"""
	
	#store the individual dimensions for the position clicked
	row, col = position_clicked
	
	# get the positions of all flags that are adjacent
	flags = get_flags((row, col), directions, public_board, len(public_board), len(public_board[0]))
	
	# if the number of adjacent flags equals (or exceeds) the number displayed, return true, else false
	if len(flags) >= public_board[row][col]:
		return True
	return False


def resolve_left_click(
		public_board: Board,
		private_board: Board,
		tile_board: list[list[Tile]],
		position_clicked: TilePosition,
		surface: Surface,
		directions: list[tuple[int, int]],
		colour_dict: dict[str: Colour],
		sfx_volume: float,
		chording: bool = False,
		puzzle: bool = False,
		tutorial: bool = False) -> tuple[bool, bool]:
	"""
		This is the program that is resolved when the user attempts to dig a tile.
		It uses a queue system to use a flood-fill style algorithm, which is useful if you need to
		resolve multiple tiles such as if you hit a 0.
		
		Inputs:
			public_board: a representation of what the user sees on the board as a 2D array
			private_board: the board to check against
			tile_board: a board containing all the tile objects
			position_clicked: the tile to resolve
			board_box: the board box object
			surface: the WIN surface
		Outputs:
			bool: whether the game should continue after this tile is clicked (ie if the user has died/ won or not)
		
	"""
	
	#initialize the queue variable. The unique parameter means that the same value cannot appear twice in the same queue
	q = Queue(unique=True)
	q.en_queue(position_clicked)
	
	#initialize variables to keep track of whether the user has died or won as a result of this click
	alive = True
	won = False
	
	#fonts to be used by the tile/ text
	font: Font = pygame.font.Font(resource_path("MainPrograms/Fonts/mine-sweeper.ttf"), int(POINT_SIZE * 4))
	text_font: Font = pygame.font.Font(resource_path("MainPrograms/Fonts/Roboto/static/Roboto-Bold.ttf"), int(POINT_SIZE * 4))
	
	high_num = -2
	
	#while there are still tiles left to resolve
	while q.get_len() > 0:
		#get a tile
		target_row, target_col = q.de_queue()
		
		#get the tile's object and value
		tile_object: Tile = tile_board[target_row][target_col]
		tile_value = private_board[target_row][target_col]
		
		# if chording enabled, and the user clicked an uncovered tile (and the current tile is the tile the user clicked
		if (target_row, target_col) == position_clicked and chording and public_board[target_row][target_col] >= 0:
			
			# if chording is possible
			if _check_chording(position_clicked, directions, public_board):
				
				# add all adjacent tiles to the queue
				for pos in tile_object.get_adjacent_tiles((target_row, target_col), directions):
					q.en_queue(pos)
			
			continue
		
		high_num = max(high_num, tile_value)
		
		#skip if tile is already resolved
		if public_board[target_row][target_col] != -2:
			continue
		
		#if the tile value is 0, add all the adjacent tiles to the queue
		if tile_value == 0 and not puzzle:
			for pos in tile_object.get_adjacent_tiles((target_row, target_col), directions):
				q.en_queue(pos)
		
		#cast its value to a string
		tile_value = str(tile_value)
		
		#if it is a mine, end the game
		if tile_value == "-1":
			
			#set the tile's value to *, which displays the mine sprite
			tile_value = "*"
			
			#set the value attribute of the tile to be a mine
			tile_object.set_value(-1)
			
			if not tutorial:
				#display text telling the user that they have died
				text: BoundingBox = BoundingBox(surface, 0, 0, POINT_SIZE, colour_dict["Background"], 0)
				text.set_pos((100 * POINT_SIZE, 20 * POINT_SIZE))
				text.set_text("You died :(", text_font)
			
			#update the tile background
			tile_object.update_colour(background_colour=colour_dict["No"])
			
			if not tutorial:
				#for every item in the private board
				for row in range(len(private_board)):
					for col in range(len(private_board)):
						
						#if there is a covered mine
						if private_board[row][col] == -1 and public_board[row][col] == -2:
							
							#display it
							tile_board[row][col].update()
							tile_board[row][col].set_value(-1)
							tile_board[row][col].set_text("*", font)
						
						#else if there is an incorrect flag
						elif private_board[row][col] != -1 and public_board[row][col] == -4:
							
							#indicate to the user
							tile_board[row][col].set_text("-", pygame.font.Font(resource_path("MainPrograms/Fonts/mine-sweeper.ttf"), int(POINT_SIZE * 4)))
			
			#set the user to be dead
			alive = False
		else:
			# update the tile background
			if tile_value == "-5":
				tile_object.update_colour(background_colour=colour_dict["Yes"])
			else:
				tile_object.update_colour(background_colour=colour_dict["Tile back"])
			
			# set the value attribute of the tile to be the relevant number
			tile_object.set_value(int(tile_value))
		
		# clear this tile
		tile_object.update()
		
		#display the value of the tile
		tile_object.set_text(tile_value, font)
		
		#update the public board
		public_board[target_row][target_col] = private_board[target_row][target_col]
	
	#check if the game is continuing, and if not, end the game
	for row in range(len(public_board)):
		for col in range(len(public_board[0])):
			if public_board[row][col] != private_board[row][col] and private_board[row][col] not in [-1, -3]:
				if high_num == -2:
					# skip sounds and return results
					return alive, won
				elif high_num >= 6:
					#any number 6 or higher plays the same sound
					high_num = "6+"
				elif high_num == 0 or high_num == -5:
					#a "0" plays the same sound as 1
					high_num = 1
				elif high_num == -1:
					high_num = "MINE"
				
				#play the sound
				press_sound = pygame.mixer.Sound(resource_path(f"MainPrograms/Sounds/MINESWEEPER SFX - {high_num} - faded.wav"))
				pygame.mixer.Sound.set_volume(press_sound, sfx_volume)
				press_sound.play()
				
				#return results
				return alive, won
	else:
		won = True
	
	if not tutorial:
		#show the user that they have won
		text: BoundingBox = BoundingBox(surface, 0, 0, POINT_SIZE, (255, 255, 255), 0)
		text.set_pos((100 * POINT_SIZE, 20 * POINT_SIZE))
		text.draw()
		text.set_text("You won :)", text_font)
		
		#play the win sound effect
		press_sound = pygame.mixer.Sound(resource_path(f"MainPrograms/Sounds/MINESWEEPER SFX - WIN - faded.wav"))
		pygame.mixer.Sound.set_volume(press_sound, sfx_volume)
		press_sound.play()
		
		#return results
		return alive, won
	else:
		return True, False


def resolve_right_click(public_board: Board,
						tile_board: list[list[Tile]],
						position_clicked: TilePosition,
						board_box: BoundingBox,
						minecount: int,
						minecount_box: BoundingBox,
						colour_dict: dict[str: Colour],
						sfx_volume: float,
						tutorial: bool = False) -> int:
	"""
		This algorithm resolves when the user attempts to flag a tile
		
		Inputs:
			public_board: a representation of what the user sees on the board as a 2D array
			tile_board: a board containing all the tile objects
			position_clicked: the tile to resolve
			board_box: the board box object
			minecount: the current displayed minecount
			minecount_box: the box that displays the minecount
		Outputs:
			int: the new minecount after this flag
	
	"""
	
	# fonts to be used by the tile/ text
	font: Font = pygame.font.Font(resource_path("MainPrograms/Fonts/mine-sweeper.ttf"), int(POINT_SIZE * 4))
	minecount_font: Font = pygame.font.Font(resource_path("MainPrograms/Fonts/Roboto/static/Roboto-Bold.ttf"), int(POINT_SIZE * 4))
	
	#If the tile is already a flag
	if public_board[position_clicked[0]][position_clicked[1]] == -4:
		
		#get the tile object at that position
		tile_object: Tile = tile_board[position_clicked[0]][position_clicked[1]]
		
		#update the public board
		public_board[position_clicked[0]][position_clicked[1]] = -2
		
		tile_object.update_colour(background_colour=colour_dict["Background"])
		
		#clear the tile
		tile_object.update()
		tile_object.set_text("", font)
		tile_object.set_value(-2)
		
		if not tutorial:
			#redraw the board box
			board_box.draw()
			
			#update and display the new minecount
			minecount += 1
			minecount_box.update()
			minecount_box.set_text(str(minecount), minecount_font)
	
	#if the tile is empty
	elif public_board[position_clicked[0]][position_clicked[1]] == -2:
		
		#get the tile object at that position
		tile_object: Tile = tile_board[position_clicked[0]][position_clicked[1]]
		
		#update the public board
		public_board[position_clicked[0]][position_clicked[1]] = -4
		
		tile_object.update_colour(background_colour=colour_dict["Flag back"])
		
		#clear the tile
		tile_object.update()
		tile_object.set_value(-4)
		tile_object.set_text("`", font)
		
		if not tutorial:
			#redraw the board box
			board_box.draw()
			
			#update and display the new minecount
			minecount -= 1
			minecount_box.update()
			minecount_box.set_text(str(minecount), minecount_font)
		
		#play sound
		press_sound = pygame.mixer.Sound(resource_path(f"MainPrograms/Sounds/MINESWEEPER SFX - HOVER.wav"))
		pygame.mixer.Sound.set_volume(press_sound, 3 * sfx_volume / 5)
		press_sound.play()
	
	#return the minecount after the click resolves
	return minecount


def resolve_left_click_offset(offset_board: Board,
							  tile_board: list[list[Tile]],
							  position_clicked: TilePosition,
							  board_box: BoundingBox,
							  colour_dict: dict[str:Colour]) -> Board:
	# If the tile is already a flag
	if offset_board[position_clicked[0]][position_clicked[1]] == 1:
		
		# get the tile object at that position
		tile_object: Tile = tile_board[position_clicked[0]][position_clicked[1]]
		
		# update the public board
		offset_board[position_clicked[0]][position_clicked[1]] = 0
		
		# clear the tile
		tile_object.update()
		
		# redraw the board box
		board_box.draw()
	
	# if the tile is empty
	elif offset_board[position_clicked[0]][position_clicked[1]] == 0:
		
		# get the tile object at that position
		tile_object: Tile = tile_board[position_clicked[0]][position_clicked[1]]
		
		# update the public board
		offset_board[position_clicked[0]][position_clicked[1]] = 1
		
		# fill the tile
		tile_object.fill(colour_dict["Yes"])
		
		# redraw the board box
		board_box.draw()
	
	return offset_board