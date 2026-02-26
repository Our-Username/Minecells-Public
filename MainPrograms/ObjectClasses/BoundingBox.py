import pygame
from pygame import Surface, font

type Coordinate = tuple[float, float]
type Colour = tuple[int, int, int]


class BoundingBox:
	def __init__(self, surface: Surface, width: float, height: float, point_size: float, border_colour: Colour, border_width: int, background_colour: Colour = (255, 255, 255)) -> None:
		"""
			Constructor method for the BoundingBox class.

			Inputs:
				- surface: the main surface which I am going to be drawing to
				- point_size: the global point size
				- width: the width of the box
				- height: the height of the box
				- border_colour: the colour of the border
				- border_width: the width of the border of the box
				- background_colour: the colour of the background of the bounding box
			Initializes:
				- self._pos: the position of the top leftmost part of the box
				- self._border_colour: the colour of the border
				- self._x_size: the width of the box
				- self._y_size: the height of the box
				- self._border_width: the width of the border of the box
				- self._background_colour: the colour of the background
				- self._WIN: the main surface which I am going to be drawing to
				- self._POINT_SIZE: the global point size
				- self._background_colour: the colour of the background of the bounding box
		"""
		self._pos: Coordinate = (0, 0)
		self._x_size: float = width
		self._y_size: float = height
		self._border_colour: Colour = border_colour
		self._background_colour: Colour = background_colour
		self._border_width: int = border_width
		self._WIN = surface
		self._POINT_SIZE: float = point_size
	
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
	
	def set_image(self, path: str) -> None:
		"""
			Defines a new image surface, and draws an image into it
			
			Inputs:
				- path: the file path to the image
			Outputs:
				- None
		"""
		
		#gets the image surface
		image_surface: Surface = pygame.image.load(path)
		
		#finds the scale factor based on the size of the bounding box versus the normal image size
		min_scale = min(((self._x_size - 2 * self._POINT_SIZE) / image_surface.get_rect()[2]),
						((self._y_size - 2 * self._POINT_SIZE) / image_surface.get_rect()[3]))
		
		#scales up the image
		image_surface: Surface = pygame.transform.smoothscale(pygame.image.load(path), (image_surface.get_rect()[2] * min_scale, image_surface.get_rect()[3] * min_scale))
		
		#centres the image within the bounding box
		image_rect = image_surface.get_rect()
		image_rect.center = (int((self._x_size / 2) + self._pos[0]), int((self._y_size // 2) + self._pos[1]))
		
		#displays the image
		self._WIN.blit(image_surface, image_rect)
	
	def set_text(self, text: str, font_input: font.Font, colour: Colour = (0, 0, 0)) -> None:
		"""
			Defines a new text object, as well as a rectangle around it such that it is centred, and displays it on the screen.
			
			Inputs:
				- text: the text to display
				- font_input: the font object to use to define the characteristics of the text.
		"""
		
		#define a text object to use to display the text
		text_obj = font_input.render(text, True, colour)
		
		#create a rectangle to use to center the text in the bounding box
		text_rect = text_obj.get_rect()
		text_rect.center = (int((self._x_size / 2) + self._pos[0]), int((self._y_size // 2) + self._pos[1]))
		
		#display the text to the screen
		self._WIN.blit(text_obj, text_rect)
	
	def set_text_left_just(self, text: str, font_input: font.Font, offset: float = 0, colour: Colour = (255, 0, 0)) -> None:
		"""
			Defines a new text object, and displays it on the screen.
			Text is left-top justified

			Inputs:
				- text: the text to display
				- font_input: the font object to use to define the characteristics of the text.
		"""
		
		# define a text object to use to display the text
		text_obj = font_input.render(text, True, colour)
		
		# create a rectangle to use to center the text in the bounding box
		text_rect = text_obj.get_rect()
		text_rect.topleft = pygame.Rect(self._pos[0] + self._POINT_SIZE, self._pos[1] + offset, self._x_size, self._y_size).topleft
		
		# display the text to the screen
		self._WIN.blit(text_obj, text_rect)
	
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