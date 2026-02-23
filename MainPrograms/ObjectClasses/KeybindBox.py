import pygame
from pygame import Surface, font
from MainPrograms.ObjectClasses.BoundingBox import BoundingBox

type Coordinate = tuple[float, float]
type Colour = tuple[int, int, int]


class KeybindBox(BoundingBox):
	def __init__(self, surface: Surface, width: float, height: float, point_size: float, colour: Colour, border_width: int, name: str, background_colour: Colour = (255, 255, 255), default_key: int = -3):
		"""
			Constructor method for the KeybindBox class.

			Inputs:
				- surface: the main surface which I am going to be drawing to
				- point_size: the global point size
				- width: the width of the box
				- height: the height of the box
				- colour: the colour of the border
				- border_width: the width of the border of the box
				- name: the name of the object
				- default_key: the default value of the key (-3 by default)
			Initializes:
				- self._pos: the position of the top leftmost part of the box
				- self._border_colour: the colour of the border
				- self._x_size: the width of the box
				- self._y_size: the height of the box
				- self._border_width: the width of the border of the box
				- self._WIN: the main surface which I am going to be drawing to
				- self._POINT_SIZE: the global point size
		"""
		super().__init__(surface, width, height, point_size, colour, border_width, background_colour=background_colour)
		self._focused: bool = False
		self._name: str = name
		self._key: int = default_key
		self._text: str = ""
		self.set_key(self._key)
	
	def check_keybind_box_clicked(self, mouse_pos: Coordinate) -> bool:
		"""
			Checks if the position where the mouse was clicked is within the keybind box

			Inputs:
				- mouse_pos: the positions that the mouse clicked
			Outputs:
				- bool: whether the position is within the keybind box
		"""
		if self._pos[0] <= mouse_pos[0] <= self._pos[0] + self._x_size:
			if self._pos[1] <= mouse_pos[1] <= self._pos[1] + self._y_size:
				return True
		return False
	
	def get_name(self) -> str:
		"""
			Getter for the self._name attribute
			
			Inputs:
				- None
			Outputs:
				- self._name: the name of the keybind box object
		"""
		return self._name
	
	def set_key(self, new_key: int) -> None:
		"""
			Setter for the self._key and self._text attributes

			Inputs:
				- new_key: the integer value of the new key
			Outputs:
				- None
		"""
		self._key = new_key
		
		if new_key == -1:
			self._text = "Right Click"
		elif new_key == -2:
			self._text = "Left Click"
		else:
			self._text = pygame.key.name(new_key).replace("_", " ").capitalize()
	
	def get_key(self) -> int:
		return self._key
	
	def set_text_value(self, text) -> None:
		self._text = text
	
	def get_text(self) -> str:
		return self._text
	
	def set_focused(self, focused: bool) -> None:
		"""
			Sets the focused state of the keybind box

			Inputs:
				- focused: the new state
			Outputs:
				- None
		"""
		self._focused = focused
	
	def get_focused(self) -> bool:
		"""
			Returns the focused state of the keybind box

			Inputs:
				- None
			Outputs:
				- self._focused: the focused state
		"""
		return self._focused
	
	def display_text(self, text: str, font_input: font.Font, colour: Colour = (0, 0, 0)) -> None:
		"""
			Defines a new text object, as well as a rectangle around it such that it is centred, and displays it on the screen.

			Inputs:
				- text: the text to display
				- font_input: the font object to use to define the characteristics of the text.
			Outputs:
				- None
		"""
		
		# define a text object to use to display the text
		text_obj = font_input.render(text, True, colour)
		
		# create a rectangle to use to center the text in the bounding box
		text_rect = text_obj.get_rect()
		text_rect.center = (int((self._x_size / 2) + self._pos[0]), int((self._y_size // 2) + self._pos[1]))
		
		# display the text to the screen
		self._WIN.blit(text_obj, text_rect)
