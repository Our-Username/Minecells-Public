import pygame
from pygame import Surface

from MainPrograms.ObjectClasses.BoundingBox import BoundingBox

type Coordinate = tuple[float, float]
type Colour = tuple[int, int, int]


class ToggleBox(BoundingBox):
	def __init__(self, surface: Surface, width: float, height: float, point_size: float, border_colour: Colour, border_width: int, name: str, primary_colour: Colour = (0, 255, 0), secondary_colour: Colour = (255, 0, 0)) -> None:
		"""
			Constructor method for the ToggleBox class.

			Inputs:
				- surface: the main surface which I am going to be drawing to
				- point_size: the global point size
				- width: the width of the box
				- height: the height of the box
				- colour: the colour of the border
				- border_width: the width of the border of the box
				- name: the name of the box
				- secondary_colour: the secondary colour of the box
			Initializes:
				- self._pos: the position of the top leftmost part of the box
				- self._primary_colour: the primary colour of the box
				- self._secondary_colour: the secondary colour of the box
				- self._x_size: the width of the box
				- self._y_size: the height of the box
				- self._border_width: the width of the border of the box
				- self._WIN: the main surface which I am going to be drawing to
				- self._POINT_SIZE: the global point size
				- self._text: the text contained within the box
				- self._active: whether the box is active or not
				- self._name: the name of the text box
				:param primary_colour:
		"""
		super().__init__(surface, width, height, point_size, border_colour, border_width)
		self._name: str = name
		self._primary_colour: Colour = primary_colour
		self._secondary_colour: Colour = secondary_colour
		self._active: bool = True
	
	def draw(self) -> None:
		"""
			Draws the box to the surface
			Inputs:
				None
			Outputs:
				None
		"""
		pygame.draw.rect(surface=self._WIN, color=self._border_colour, rect=(self._pos[0], self._pos[1], self._x_size, self._y_size),
						 width=self._border_width)
	
	def update(self) -> None:
		"""
			Draws the box to the surface, clearing whatever is behind it
			Inputs:
				None
			Outputs:
				None
		"""
		pygame.draw.rect(surface=self._WIN, color=self._primary_colour, rect=(self._pos[0], self._pos[1], self._x_size, self._y_size))
		pygame.draw.rect(surface=self._WIN, color=self._border_colour, rect=(self._pos[0], self._pos[1], self._x_size, self._y_size),
						 width=self._border_width)
	
	def _draw_with_colour(self, colour: Colour = None):
		"""
			Updates the box with the given colour
			
			Inputs:
				- colour: the colour to draw the box with (primary colour by default)
			Outputs:
				- None
		"""
		if colour is None:
			colour = self._primary_colour
		
		pygame.draw.rect(surface=self._WIN, color=colour, rect=(self._pos[0], self._pos[1], self._x_size, self._y_size))
		pygame.draw.rect(surface=self._WIN, color=self._border_colour, rect=(self._pos[0], self._pos[1], self._x_size, self._y_size),
						 width=self._border_width)
	
	def check_toggle_box_clicked(self, mouse_pos: Coordinate) -> bool:
		"""
			Checks if the position where the mouse was clicked is within the toggle box

			Inputs:
				- mouse_pos: the positions that the mouse clicked
			Outputs:
				- bool: whether the position is within the toggle box
		"""
		if self._pos[0] <= mouse_pos[0] <= self._pos[0] + self._x_size:
			if self._pos[1] <= mouse_pos[1] <= self._pos[1] + self._y_size:
				return True
		return False
	
	def on_click(self) -> None:
		"""
			Toggles between active and inactive, and draws the box with the relevant colour
			
			Inputs:
				- None
			Outputs:
				- None
		"""
		#if active, make inactive
		if self._active:
			self._active = False
			self._draw_with_colour(self._secondary_colour)
		
		# if inactive, make active
		else:
			self._active = True
			self._draw_with_colour(self._primary_colour)
	
	def get_active(self) -> bool:
		return self._active
	
	def initial_draw(self, active: bool = True) -> None:
		"""
			Sets whether the box is active once initially drawn, and draws the box
			
			Inputs:
				- active: whether the box is to be active at the start
			Outputs
				- None
		
		"""
		self._active = active
		
		if self._active:
			self._draw_with_colour(self._primary_colour)
		else:
			self._draw_with_colour(self._secondary_colour)
	
	def get_name(self) -> str:
		return self._name
	
	def update_colour(self, *, primary_colour: Colour = None, secondary_colour: Colour = None, border_colour: Colour = None) -> None:
		if primary_colour is not None:
			self._background_colour = primary_colour
		if secondary_colour is not None:
			self._secondary_colour = secondary_colour
		if border_colour is not None:
			self._border_colour = border_colour