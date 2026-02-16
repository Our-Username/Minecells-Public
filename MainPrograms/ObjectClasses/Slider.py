import pygame
from pygame import Surface

type Coordinate = tuple[float, float]
type Colour = tuple[int, int, int]


class Slider:
	def __init__(self, surface: Surface, width: float, point_size: float, line_colour: Colour, line_width: int) -> None:
		"""
			Constructor method for the Slider class.

			Inputs:
				- surface: the main surface which I am going to be drawing to
				- point_size: the global point size
				- width: the length of the slider
				- line_colour: the colour of the line
				- line_width: the thickness of the slider
			Initializes:
				- self._pos: the position of the top leftmost part of the box
				- self._line_colour: the colour of the border
				- self._x_size: the width of the box
				- self._line_width: the width of the border of the box
				- self._WIN: the main surface which I am going to be drawing to
				- self._POINT_SIZE: the global point size
		"""
		self._pos: Coordinate = (0, 0)
		self._x_size: float = width
		self._line_colour: Colour = line_colour
		self._line_width: int = line_width
		self._WIN = surface
		self._POINT_SIZE: float = point_size
	
	def set_pos(self, new_pos: Coordinate) -> None:
		"""
			Setter method for self._pos

			Inputs:
				- new_pos: the new position of the box
			Modifies:
				- self._pos: the position of the top leftmost part of the box
		"""
		self._pos = new_pos
	
	def get_pos(self) -> Coordinate:
		"""
			Getter method for self._pos

			Inputs:
				- None
			Outputs:
				- self._pos: the position of the slide
		"""
		return self._pos
	
	def get_length(self) -> float:
		"""
			Getter for the self._x_size attribute
			
			Inputs:
				- None
			Outputs:
				- self._x_size: the length of the slide
		"""
		return self._x_size
	
	def get_percent(self, orb_x: float) -> float:
		"""
			Gives the position of the orb's location as a percentage of the slider's length
			
			Input:
				- orb_x: the x-position of the orb
			Output:
				- float: the percentage generated from the orb's position
		
		"""
		#cap between 0 and 100
		if orb_x - self._pos[0] < 0:
			return 0.0
		elif orb_x - self._pos[0] > self._x_size:
			return 100.0
		return round((orb_x - self._pos[0]) * 100 / self._x_size, 3)
	
	def draw(self) -> None:
		"""
			Draws the slider line to the surface
			Inputs:
				None
			Outputs:
				None
		"""
		pygame.draw.rect(surface=self._WIN, color=self._line_colour, rect=(self._pos[0], self._pos[1], self._x_size, self._line_width),
						 width=self._line_width)


class SliderOrb:
	def __init__(self, surface: Surface, radius: float, point_size: float, border_colour: Colour, border_width: int, background_colour: Colour = (255, 255, 255)) -> None:
		"""
			Constructor method for the SliderOrb class.

			Inputs:
				- surface: the main surface which I am going to be drawing to
				- point_size: the global point size
				- radius: the radius of the orb
				- border_colour: the colour of the border
				- border_width: the width of the border of the orb
				- background_colour: the colour of the background (default white)
			Initializes:
				- self._pos: the position of the centre of the orb
				- self._border_colour: the colour of the border
				- self._radius: the radius of the orb
				- self._border_width: the width of the border of the orb
				- self._background_colour: the colour of the background
				- self._WIN: the main surface which I am going to be drawing to
				- self._POINT_SIZE: the global point size
		"""
		self._pos: Coordinate = (0, 0)
		self._radius: float = radius
		self._border_colour: Colour = border_colour
		self._background_colour: Colour = background_colour
		self._border_width: int = border_width
		self._WIN = surface
		self._POINT_SIZE: float = point_size
	
	def draw(self) -> None:
		"""
			Draws the slider line to the surface
			Inputs:
				None
			Outputs:
				None
		"""
		pygame.draw.circle(surface=self._WIN, color=self._background_colour, center=self._pos, radius=self._radius)
		pygame.draw.circle(surface=self._WIN, color=self._border_colour, center=self._pos, radius=self._radius, width=self._border_width)
	
	def clear(self) -> None:
		pygame.draw.circle(surface=self._WIN, color=self._background_colour, center=self._pos, radius=self._radius)
	
	def move(self, new_position) -> None:
		self._pos = new_position, self._pos[1]
		self.draw()
	
	def check_clicked(self, mouse_pos: Coordinate) -> bool:
		"""
			Checks if the orb has been clicked
			
			Inputs:
				- mouse_pos: the position of the mouse on the screen
			Outputs:
				- bool: whether the orb has been clicked
		
		"""
		#pythagoras to get distance
		distance_from_centre: float = ((mouse_pos[0] - self._pos[0]) ** 2 + (mouse_pos[1] - self._pos[1]) ** 2) ** 0.5
		
		if distance_from_centre <= self._radius:
			return True
		return False
	
	def set_pos(self, new_pos: Coordinate) -> None:
		"""
			Setter method for self._pos

			Inputs:
				- new_pos: the new position of the box
			Modifies:
				- self._pos: the position of the top leftmost part of the box
		"""
		self._pos = new_pos
	
	def get_pos(self) -> Coordinate:
		"""
			Getter method for self._pos

			Inputs:
				- None
			Outputs:
				- self._pos: the position of the slide
		"""
		return self._pos