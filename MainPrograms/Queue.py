from typing import Any


class Queue:
	def __init__(self, unique: bool = False) -> None:
		"""
			Constructor method for the Queue class
			
			Inputs:
				- unique: default False, decides whether all items in the queue have to be unique
			Initializes:
				- self._q: the queue stored
				- self._unique: decides whether all items in the queue have to be unique
		
		"""
		self._q: list = []
		self._unique: bool = unique
	
	def en_queue(self, item: Any) -> None:
		"""
			Add an item to the end of the queue
			
			Inputs:
				- item: the item to add
			Outputs:
				- None
		"""
		if self._unique:
			if item not in self._q:
				self._q.append(item)
		else:
			self._q.append(item)
	
	def de_queue(self) -> Any:
		"""
			Removes an item from the front of the queue, and returns it

			Inputs:
				- None
			Outputs:
				- The item removed
		"""
		if self.get_len() == 0:
			return None
		return self._q.pop(0)
	
	def get_queue(self) -> list:
		"""
			Gets the queue stored
		"""
		return self._q
	
	def get_len(self) -> int:
		"""
			Gets the length of the queue
		"""
		return len(self._q)
		