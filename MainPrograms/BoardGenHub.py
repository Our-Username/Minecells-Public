from BoardGeneratorPrograms.BoardGenerator import BoardGenerator
from BoardGeneratorPrograms.ChainBoardGenerator import ChainBoardGenerator
from BoardGeneratorPrograms.OffsetBoardGenerator import OffsetBoardGenerator
from BoardGeneratorPrograms.OffsetPuzzleGenerator import OffsetPuzzleGenerator
from BoardGeneratorPrograms.PuzzleBoardGenerator import PuzzleBoardGenerator
from BoardGeneratorPrograms.SpaceBoardGenerator import SpaceBoardGenerator

import multiprocessing as mp

type TilePosition = tuple[int, int]
type Board = list[list[int]]


class BoardGenHub:
	def __init__(self) -> None:
		pass
	
	@staticmethod
	def gen_board(board_generator: str, *args) -> tuple[Board, set[TilePosition] | None]:
		board_gen = None
		
		match board_generator:
			case "Standard":
				board_gen = BoardGenerator(*args)
			case "Chain":
				board_gen = ChainBoardGenerator(*args)
			case "Offset":
				board_gen = OffsetBoardGenerator(*args)
			case "Offset Puzzle":
				board_gen = OffsetPuzzleGenerator(*args)
			case "Puzzle":
				board_gen = PuzzleBoardGenerator(*args)
			case "Space":
				board_gen = SpaceBoardGenerator(*args)
		
		revealed_tiles: set[TilePosition] | None = board_gen.generate_no_guess_board()
		
		return board_gen.get_board(), revealed_tiles
	
	@staticmethod
	def gen_board_parallel(halt_event: mp.Event, board_generator: str, *args) -> tuple[Board, set[TilePosition] | None]:
		"""
			Worker function to generate boards in parallel
			
			Inputs:
				- board_generator: the board generator to use
				- start_event: the collective event to indicate to other processes when one is done
				- result_q: the queue of return values
				- args: the parameters to be used by the board generator
			Outputs:
				- board_gen.get_board(): the board produced
				- revealed_tiles: any tiles that start off as revealed for a puzzle board
		"""
		
		board_gen = None
		
		if board_generator == "":
			board_generator = "Standard"
		
		#select the board generator class
		match board_generator:
			case "Standard":
				board_gen = BoardGenerator(*args)
			case "Chain":
				board_gen = ChainBoardGenerator(*args)
			case "Offset":
				board_gen = OffsetBoardGenerator(*args)
			case "Offset Puzzle":
				board_gen = OffsetPuzzleGenerator(*args)
			case "Puzzle":
				board_gen = PuzzleBoardGenerator(*args)
			case "Space":
				board_gen = SpaceBoardGenerator(*args)
		
		#generate the board
		revealed_tiles: set[TilePosition] | None = board_gen.generate_no_guess_board_parallel(halt_event)
		
		#return results
		return board_gen.get_board(), revealed_tiles
	
	@staticmethod
	def worker(task_queue: mp.Queue, halt_event: mp.Event, result_queue: mp.Queue) -> None:
		"""
			The worker process
			
			Inputs:
				- task_queue: the queue the worker will read from
				- halt_event: the event which signals that the worker should stop its current task
				- result_queue: the queue to return the task's result from
			Outputs:
				- None
		"""
		
		#while the worker is being run
		while True:
			
			#wait for and get the next task
			task = task_queue.get()
			
			#if the task is None (ie an arbitrary value to kill the process), kill the worker
			if task is None:
				break
			
			#reset the halt_event
			halt_event.clear()
			
			#do the task
			func, *args = task
			result = func(halt_event, *args)
			
			#if there is a result, put it in the result queue
			if result is not None:
				result_queue.put(result)
	
	def init_parallel(self) -> tuple[list[mp.Process], mp.Queue, mp.Queue]:
		"""
			Completes the initial setup for parallel processing.
			
			Inputs:
				- None
			Outputs:
				- workers: a list of all the worker processes
				- task_queue: the queue the workers will look at to get tasks
				- result_queue: the queue the workers will return values to
		"""
		
		#initializes the task queue for workers to get tasks from
		task_queue: mp.Queue = mp.Queue()
		
		# initializes the result queue for workers to return values to
		result_queue: mp.Queue = mp.Queue()
		
		#initializes the event that signals that the workers should stop their current task
		halt_event: mp.Event = mp.Event()
		
		#initializes a list of workers
		workers = [mp.Process(target=self.worker, args=(task_queue, halt_event, result_queue)) for _ in range(mp.cpu_count())]
		
		#starts all the worker processes
		for worker in workers:
			worker.start()
		
		return workers, task_queue, result_queue
			
	