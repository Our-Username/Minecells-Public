import pygame
from pygame import Surface, font

type Coordinate = tuple[float, float]
type Colour = tuple[int, int, int]


class Button:
	def __init__(self, surface: Surface, point_size: float, width: float, height: float, colour: Colour, name: str, border_width: int = 0, background_colour: Colour = (255, 255, 255)) -> None:
		"""
			Constructor method for the Button class.
			
			Inputs:
				surface: the main surface which I am going to be drawing to
				point_size: the global point size
				width: the width of the button
				height: the height of the button
				colour: the colour of the button
				sprite: the sprite of the button (if any)
			Initializes:
				self._pos: the position of the top leftmost part of the button
				self._border_colour: the colour of the button
				self._sprite: the sprite of the button (if any)
				self._x_size: the width of the button
				self._y_size: the height of the button
				self._WIN: the main surface which I am going to be drawing to
				self._POINT_SIZE: the global point size
		"""
		
		#initialize variables
		self._pos: Coordinate = (0, 0)  #(0, 0) by default, and can be changed through a method
		self._border_colour: Colour = colour
		self._border_width = border_width
		self._x_size: float = width
		self._y_size: float = height
		self._WIN: Surface = surface
		self._POINT_SIZE: float = point_size
		self._name: str = name
		self._background_colour: Colour = background_colour
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
	
	def set_pos(self, new_pos: Coordinate) -> None:
		"""
			Setter method for self._pos
			
			Inputs:
				new_pos: the new position of the button
			Modifies:
				self._pos: the position of the top leftmost part of the button
		"""
		self._pos = new_pos
	
	def get_name(self) -> str:
		"""
			Getter for salf._name attribute
			
			Inputs:
				- None
			Outputs:
				-self._name: the name of the button
		"""
		return self._name
	
	def draw(self) -> None:
		"""
			Draws the button to the surface
			
			Inputs:
				None
			Outputs:
				None
		"""
		if self._border_width > 0:
			pygame.draw.rect(surface=self._WIN, color=self._border_colour, rect=(self._pos[0], self._pos[1], self._x_size, self._y_size), width=self._border_width)
		else:
			pygame.draw.rect(surface=self._WIN, color=self._border_colour, rect=(self._pos[0], self._pos[1], self._x_size, self._y_size))
	
	def set_image(self, image_path: str) -> None:
		image_surface = pygame.transform.scale(pygame.image.load(image_path), (8 * self._POINT_SIZE, 8 * self._POINT_SIZE))
		self._WIN.blit(image_surface, (self._pos[0] + self._POINT_SIZE, self._pos[1] + self._POINT_SIZE))
	
	def update(self) -> None:
		"""
			Draws the box to the surface, clearing whatever is behind it
			
			Inputs:
				None
			Outputs:
				None
		"""
		pygame.draw.rect(surface=self._WIN, color=self._background_colour, rect=(self._pos[0], self._pos[1], self._x_size, self._y_size))
		
		if self._border_width > 0:
			pygame.draw.rect(surface=self._WIN, color=self._border_colour, rect=(self._pos[0], self._pos[1], self._x_size, self._y_size), width=self._border_width)
		else:
			pygame.draw.rect(surface=self._WIN, color=self._border_colour, rect=(self._pos[0], self._pos[1], self._x_size, self._y_size))
	
	def check_button_click(self, mouse_pos: Coordinate) -> bool:
		"""
			Checks if the position where the mouse was clicked is within the button
			
			Inputs:
				- mouse_pos: the positions that the mouse clicked
			Outputs:
				- bool: whether the position is within the button
		"""
		if self._pos[0] <= mouse_pos[0] <= self._pos[0] + self._x_size:
			if self._pos[1] <= mouse_pos[1] <= self._pos[1] + self._y_size:
				return True
		return False
	
	def get_width(self) -> float:
		"""
			Getter for self._x_size
			
			Inputs:
				None
			Outputs:
				- self._x_size: the width of the button
		"""
		return self._x_size
	
	def get_height(self) -> float:
		"""
			Getter for self._y_size

			Inputs:
				None
			Outputs:
				- self._y_size: the height of the button
		"""
		return self._y_size
	
	@staticmethod
	def on_click(event):
		event()
	
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