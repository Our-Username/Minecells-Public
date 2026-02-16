import math

import pygame
from pygame import Surface, font

type Coordinate = tuple[float, float]
type Colour = tuple[int, int, int]
type TilePosition = tuple[int, int]


class Tile:
	def __init__(self, surface: Surface, tile_size: float, point_size: float, border_colour: Colour, border_width: int, tile_coordinate: TilePosition, rows: int, cols: int, text_colour_start: Colour, text_colour_end: Colour, background_colour: Colour = (255, 255, 255)) -> None:
		"""
			Constructor method for the Tile class.

			Inputs:
				surface: the main surface which I am going to be drawing to
				point_size: the global point size
				tile_size: the size of the tile
				colour: the colour of the border
				border_width: the width of the border of the tile
				tile_coordinate: the coordinate of the tile in the board
			Initializes:
				self._pos: the position of the top leftmost part of the tile
				self._border_colour: the colour of the border
				self._x_size: the width of the tile
				self._y_size: the height of the tile
				self._border_width: the width of the border of the tile
				self._WIN: the main surface which I am going to be drawing to
				self._POINT_SIZE: the global point size
				self._tile_coordinate: the coordinate of the tile in the board
		"""
		self._pos: Coordinate = (0, 0)
		self._x_size: float = tile_size
		self._y_size: float = tile_size
		self._border_colour: Colour = border_colour
		self._border_width: int = border_width
		self._WIN = surface
		self._POINT_SIZE: float = point_size
		self._tile_coordinate: TilePosition = tile_coordinate
		self._directions: list[TilePosition] = [(x, y) for x in [-1, 0, 1] for y in [-1, 0, 1]]
		self._n_cols: int = cols  # initialize variables from parameters
		self._n_rows: int = rows
		self._value: int = -2
		self._text_colour_start: Colour = text_colour_start
		self._text_colour_end: Colour = text_colour_end
		self._background_colour: Colour = background_colour
	
	def set_surface(self, surface: Surface) -> None:
		self._WIN = surface
	
	def set_pos(self, new_pos: Coordinate) -> None:
		"""
			Setter method for self._pos

			Inputs:
				new_pos: the new position of the box
			Modifies:
				self._pos: the position of the top leftmost part of the box
		"""
		self._pos = new_pos
	
	def get_tile_pos(self) -> TilePosition:
		"""
			Setter method for self._pos

			Inputs:
				None
			Outputs
				self._tile_coordinate: the coordinate of the tile
		"""
		return self._tile_coordinate
	
	def set_point_size(self, point_size) -> None:
		self._POINT_SIZE = point_size
	
	def draw(self) -> None:
		"""
			Draws the tile to the surface
			Inputs:
				None
			Outputs:
				None
		"""
		pygame.draw.rect(surface=self._WIN, color=self._border_colour, rect=(self._pos[0], self._pos[1], self._x_size, self._y_size),
						 width=self._border_width)
	
	def update(self) -> None:
		"""
			Draws the tile to the surface, clearing whatever is behind it
			Inputs:
				None
			Outputs:
				None
		"""
		pygame.draw.rect(surface=self._WIN, color=self._background_colour, rect=(self._pos[0], self._pos[1], self._x_size, self._y_size))
		pygame.draw.rect(surface=self._WIN, color=self._border_colour, rect=(self._pos[0], self._pos[1], self._x_size, self._y_size),
						 width=self._border_width)
	
	def fill(self, colour) -> None:
		"""
			Draws the tile to the surface, clearing whatever is behind it
			Inputs:
				None
			Outputs:
				None
		"""
		pygame.draw.rect(surface=self._WIN, color=colour, rect=(self._pos[0], self._pos[1], self._x_size, self._y_size))
		pygame.draw.rect(surface=self._WIN, color=self._border_colour, rect=(self._pos[0], self._pos[1], self._x_size, self._y_size),
						 width=self._border_width)
	
	def set_text(self, text: str, font_input: font.Font) -> None:
		"""
			Defines a new text object, as well as a rectangle around it such that it is centred, and displays it on the screen.

			Inputs:
				- text: the text to display
				- font_input: the font object to use to define the characteristics of the text.
		"""
		
		#set colour depending on the values of the tile start and end colour values
		if self._value == -4 or self._value == -1:
			if self._background_colour == (150, 0, 0):
				colour: Colour = (0, 0, 0)
			else:
				colour: Colour = (150, 0, 0)
		elif self._value == -2 or self._value == -5:
			return
		else:
			colour: Colour = (
				min(255, max(0, int(self._text_colour_start[0] + 2 * math.log10(self._value + 1) * (self._text_colour_end[0] - self._text_colour_start[0])))),
				min(255, max(0, int(self._text_colour_start[1] + 2 * math.log10(self._value + 1) * (self._text_colour_end[1] - self._text_colour_start[1])))),
				min(255, max(0, int(self._text_colour_start[2] + 2 * math.log10(self._value + 1) * (self._text_colour_end[2] - self._text_colour_start[2])))),
			)
		
		# define a text object to use to display the text
		text_obj = font_input.render(text, True, colour)
		
		# create a rectangle to use to center the text in the bounding box
		text_rect = text_obj.get_rect()
		text_rect.center = (int((self._x_size / 2) + self._pos[0]), int((self._y_size / 2) + self._pos[1]))
		
		# display the text to the screen
		self._WIN.blit(text_obj, text_rect)
	
	def on_click(self) -> TilePosition:
		return self._tile_coordinate
	
	def check_tile_clicked(self, mouse_pos: Coordinate, zoom: float, offset: tuple[float, float]) -> bool:
		"""
			Checks if the position where the mouse was clicked is within the tile

			Inputs:
				- mouse_pos: the positions that the mouse clicked
			Outputs:
				- bool: whether the position is within the tile
		"""
		x_low = self._pos[0] * zoom - offset[0]
		x_high = (self._pos[0] + self._x_size) * zoom - offset[0]
		
		y_low = self._pos[1] * zoom - offset[1]
		y_high = (self._pos[1] + self._y_size) * zoom - offset[1]
		
		if x_low <= mouse_pos[0] < x_high:
			if y_low <= mouse_pos[1] < y_high:
				return True
		return False
	
	def get_adjacent_tiles(self, pos: TilePosition, directions: list[tuple[int, int]]) -> set[TilePosition]:
		"""
			Gives the positions of the adjacent tiles

			Inputs:
				- pos: the target tile position
			Returns:
				- output_set: the list of adjacent tiles
		"""
		output_set: set[TilePosition] = set()  # initialise output set
		
		for row, col in directions:  # for each adjacent tile
			if 0 <= pos[0] + row < self._n_rows and 0 <= pos[1] + col < self._n_cols:  # if position within the board
				output_set.add((pos[0] + row, pos[1] + col))  # add it to the set
		
		return output_set
	
	def set_value(self, value: int) -> None:
		self._value = value
	
	def get_value(self) -> int:
		return self._value
	
	def update_colour(self, *, background_colour: Colour = None, border_colour: Colour = None) -> None:
		if background_colour is not None:
			self._background_colour = background_colour
		if border_colour is not None:
			self._border_colour = border_colour