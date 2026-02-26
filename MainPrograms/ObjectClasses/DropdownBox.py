import pygame
from pygame import Surface, font
from MainPrograms.ObjectClasses.TextInputBox import TextInputBox

type Coordinate = tuple[float, float]
type Colour = tuple[int, int, int]


class DropdownBox(TextInputBox):
	def __init__(self, surface: Surface, width: float, height: float, point_size: float, colour: Colour, border_width: int, name: str, background_colour: Colour = (255, 255, 255)):
		"""
			Constructor method for the DropdownBox class.

			Inputs:
				- surface: the main surface which I am going to be drawing to
				- point_size: the global point size
				- width: the width of the box
				- height: the height of the box
				- colour: the colour of the border
				- border_width: the width of the border of the box
				- name: the name of the box
				- background_colour: the colour of the background of the dropdown box
			Initializes:
				- self._pos: the position of the top leftmost part of the box
				- self._border_colour: the colour of the border
				- self._x_size: the width of the box
				- self._y_size: the height of the box
				- self._border_width: the width of the border of the box
				- self._WIN: the main surface which I am going to be drawing to
				- self._POINT_SIZE: the global point size
				- self._text: the text contained within the textbox
				- self._focused: whether the box is focused or not
				- self._name: the name of the text box
				- self._background_colour: the colour of the background of the dropdown box
		"""
		super().__init__(surface, width, height, point_size, colour, border_width, name, background_colour=background_colour)
		self.option: str = name.capitalize()
	
	def check_drop_box_clicked(self, mouse_pos: Coordinate) -> bool:
		"""
			Checks if the position where the mouse was clicked is within the dropdown box

			Inputs:
				- mouse_pos: the positions that the mouse clicked
			Outputs:
				- bool: whether the position is within the dropdown box
		"""
		if self._pos[0] <= mouse_pos[0] <= self._pos[0] + self._x_size:
			if self._pos[1] <= mouse_pos[1] <= self._pos[1] + self._y_size:
				return True
		return False
	
	def set_current_option(self, option) -> None:
		"""
			Setter for the self.option attribute
			
			Inputs:
				- option: the new option to set the dropdown box to
			Outputs:
				- None
		"""
		self.option = option
	
	def get_current_option(self) -> str:
		"""
			Getter for the self.option attribute

			Inputs:
				- None
			Outputs:
				- self.option: the  option the dropdown box displays
		"""
		return self.option
	
	def update_colour(self, *, background_colour: Colour = None, border_colour: Colour = None) -> None:
		"""
			Updates the colour of the box. If None is passed, keep the current colour.
			
			Inputs:
				- background_colour: the new colour for the background (default None)
				- border_colour: the new colour for the border (default None)
			Outputs:
				- None
		"""
		if background_colour is not None:
			self._background_colour = background_colour
		if border_colour is not None:
			self._border_colour = border_colour


class DropdownOption:
	def __init__(self, surface: Surface, width: float, height: float, point_size: float, border_colour: Colour, border_width: int, name: str, background_colour: Colour):
		"""
			Constructor method for the DropdownOption class.

			Inputs:
				- surface: the main surface which I am going to be drawing to
				- point_size: the global point size
				- width: the width of the box
				- height: the height of the box
				- colour: the colour of the border
				- border_width: the width of the border of the box
			Initializes:
				- self._pos: the position of the top leftmost part of the box
				- self._border_colour: the colour of the border
				- self._x_size: the width of the box
				- self._y_size: the height of the box
				- self._border_width: the width of the border of the box
				- self._WIN: the main surface which I am going to be drawing to
				- self._POINT_SIZE: the global point size
				- self._focused: whether the box is focused or not
				- self._name: the name of the text box
		"""
		self._pos: Coordinate = (0, 0)
		self._x_size: float = width
		self._y_size: float = height
		self._border_colour: Colour = border_colour
		self._border_width: int = border_width
		self._WIN = surface
		self._POINT_SIZE: float = point_size
		self._text: str = ""
		self._focused: bool = False
		self._name = name
		self._visible: bool = False
		self._background_colour: Colour = background_colour
	
	def check_drop_option_clicked(self, mouse_pos: Coordinate) -> bool:
		"""
			Checks if the position where the mouse was clicked is within the dropdown option box

			Inputs:
				- mouse_pos: the positions that the mouse clicked
			Outputs:
				- bool: whether the position is within the text dropdown option box
		"""
		if self._pos[0] <= mouse_pos[0] <= self._pos[0] + self._x_size:
			if self._pos[1] <= mouse_pos[1] <= self._pos[1] + self._y_size:
				return True
		return False
	
	def get_name(self) -> str:
		return self._name
	
	def set_visible(self, visible: bool) -> None:
		self._visible = visible
	
	def get_visible(self) -> bool:
		return self._visible
	
	def set_pos(self, new_pos: Coordinate) -> None:
		"""
			Setter method for self._pos

			Inputs:
				new_pos: the new position of the box
			Modifies:
				self._pos: the position of the top leftmost part of the box
		"""
		self._pos = new_pos
	
	def draw(self) -> None:
		"""
			Draws the box to the surface
			
			Inputs:
				- None
			Outputs:
				- None
		"""
		pygame.draw.rect(surface=self._WIN, color=self._border_colour, rect=(self._pos[0], self._pos[1], self._x_size, self._y_size),
						 width=self._border_width)
	
	def update(self) -> None:
		"""
			Draws the box to the surface, clearing whatever is behind it
			
			Inputs:
				- None
			Outputs:
				- None
		"""
		pygame.draw.rect(surface=self._WIN, color=self._background_colour, rect=(self._pos[0], self._pos[1], self._x_size, self._y_size))
		pygame.draw.rect(surface=self._WIN, color=self._border_colour, rect=(self._pos[0], self._pos[1], self._x_size, self._y_size),
						 width=self._border_width)
	
	def set_text(self, text: str, font_input: font.Font, colour: Colour = (0, 0, 0)) -> None:
		"""
			Defines a new text object, as well as a rectangle around it such that it is centred, and displays it on the screen.

			Inputs:
				- text: the text to display
				- font_input: the font object to use to define the characteristics of the text.
		"""
		
		# define a text object to use to display the text
		text_obj = font_input.render(text, True, colour)
		
		# create a rectangle to use to center the text in the bounding box
		text_rect = text_obj.get_rect()
		text_rect.center = (int((self._x_size / 2) + self._pos[0]), int((self._y_size // 2) + self._pos[1]))
		
		# display the text to the screen
		self._WIN.blit(text_obj, text_rect)
	
	def update_colour(self, *, background_colour: Colour = None, border_colour: Colour = None) -> None:
		if background_colour is not None:
			self._background_colour = background_colour
		if border_colour is not None:
			self._border_colour = border_colour