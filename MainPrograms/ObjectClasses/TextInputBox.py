from MainPrograms.ObjectClasses.BoundingBox import BoundingBox
from pygame import Surface, font

type Coordinate = tuple[float, float]
type Colour = tuple[int, int, int]


class TextInputBox(BoundingBox):
	def __init__(self, surface: Surface, width: float, height: float, point_size: float, border_colour: Colour, border_width: int, name: str, background_colour: Colour = (255, 255, 255)) -> None:
		"""
			Constructor method for the TextInputBox class.

			Inputs:
				- surface: the main surface which I am going to be drawing to
				- point_size: the global point size
				- width: the width of the box
				- height: the height of the box
				- border_colour: the colour of the border
				- border_width: the width of the border of the box
				- name: the name of the box
				- background_colour: the colour of the background of the box
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
				- self._active: whether the box appears and can be interacted with on the screen
		"""
		super().__init__(surface, width, height, point_size, border_colour, border_width, background_colour=background_colour)
		self._text: str = ""
		self._focused: bool = False
		self._name: str = name
		self._active: bool = True
	
	def get_active(self) -> bool:
		"""
			A getter for the self._active attribute
			
			Inputs:
				- None
			Outputs:
				- self._active: whether the object does something on click
		"""
		return self._active
	
	def set_active(self, active: bool) -> None:
		"""
			A setter for the self._active attribute

			Inputs:
				- active: the new value for self._active
			Outputs:
				- None
		"""
		self._active = active
	
	def add_char(self, character: str) -> None:
		"""
			Adds a character to the text
			
			Inputs:
				- character: the character to add
			Outputs:
				- None
		
		"""
		self._text += character
	
	def remove_char(self) -> None:
		"""
			Removes a character from the end of the text

			Inputs:
				- None
			Outputs:
				- None

		"""
		self._text = self._text[:-1]
	
	def get_text(self) -> str:
		"""
			Removes a character from the end of the text

			Inputs:
				- None
			Outputs:
				- self._text: the text displayed
		"""
		return self._text
	
	def set_focused(self, focused: bool) -> None:
		"""
			Sets the focused state of the text box

			Inputs:
				- focused: the new state
			Outputs:
				- None
		"""
		self._focused = focused
	
	def get_focused(self) -> bool:
		"""
			Returns the focused state of the text box

			Inputs:
				- None
			Outputs:
				- self._focused: the focused state
		"""
		return self._focused
	
	def get_name(self) -> str:
		"""
			Returns the name of the text box

			Inputs:
				- None
			Outputs:
				- self._name: the text box name
		"""
		return self._name
	
	def check_text_box_clicked(self, mouse_pos: Coordinate) -> bool:
		"""
			Checks if the position where the mouse was clicked is within the text box

			Inputs:
				- mouse_pos: the positions that the mouse clicked
			Outputs:
				- bool: whether the position is within the text box
		"""
		if self._pos[0] <= mouse_pos[0] <= self._pos[0] + self._x_size:
			if self._pos[1] <= mouse_pos[1] <= self._pos[1] + self._y_size:
				return True
		return False
	
	def display_text(self, font_input: font.Font, colour: Colour = (0, 0, 0)) -> None:
		"""
			Defines a new text object, as well as a rectangle around it such that it is centred, and displays it on the screen.

			Inputs:
				- text: the text to display
				- font_input: the font object to use to define the characteristics of the text.
		"""
		
		# define a text object to use to display the text
		text_obj = font_input.render(self._text, True, colour)
		
		# create a rectangle to use to center the text in the bounding box
		text_rect = text_obj.get_rect()
		text_rect.center = (int((self._x_size / 2) + self._pos[0]), int((self._y_size // 2) + self._pos[1]))
		
		# display the text to the screen
		self._WIN.blit(text_obj, text_rect)
	
	def display_given_text(self, text: str, font_input: font.Font, colour: Colour = (0, 0, 0)) -> None:
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