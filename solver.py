from enum import Enum
from typing import Any
import pyautogui
import time
import keyboard
import random

from pyscreeze import Box

from variables import *

class TileKind(Enum):
	UNKNOWN = 0
	GLIMMER = 1
	GLOOM = 2

class Tile:
	def __init__(self, kind: TileKind = TileKind.UNKNOWN, box: Box | None = None):
		self.kind: TileKind = kind
		self.box: Box | None = box

class GameBoard:
	def __init__(self):
		self.WIN_TILE_KIND = TileKind.GLIMMER
		self.grid: list[list[Tile]] = [
			[Tile()] * 5,
			[Tile()] * 6,
			[Tile()] * 7,
			[Tile()] * 8,
			[Tile()] * 9,
			[Tile()] * 8,
			[Tile()] * 7,
			[Tile()] * 6,
			[Tile()] * 5,
		]
		self.find_all()
	
	def is_solved(self) -> bool:
		solved_tile_count = 0
		for row in self.grid:
			for tile in row:
				if tile.kind == self.WIN_TILE_KIND:
					solved_tile_count += 1
		return solved_tile_count == 61

	def __str__(self):
		text = ""
		i = 4
		for row in self.grid:
			text += " " * abs(i)
			for tile in row:
				if tile.kind == TileKind.GLOOM:
					text += "o "
				elif tile.kind == TileKind.GLIMMER:
					text += "i "
				elif tile.kind == TileKind.UNKNOWN:
					text += "? "
				else:
					raise ValueError("Developer error: undefined tile!")
			text += "\n"
			i -= 1
		return text

	def find_all(self):
		PIXEL_EPSILON: int = 7
		raw_inferred_tiles: list[Tile] = []
		for box in pyautogui.locateAllOnScreen("gloom.png", confidence=0.73):
			raw_inferred_tiles.append(Tile(TileKind.GLOOM, box))
		for box in pyautogui.locateAllOnScreen("glimmer.png", confidence=0.73):
			raw_inferred_tiles.append(Tile(TileKind.GLIMMER, box))

		sorted_tiles = sorted(raw_inferred_tiles, key=lambda tile: (tile.box.top // PIXEL_EPSILON, tile.box.left // PIXEL_EPSILON) if tile.box is not None else -1)

		deduped_tiles: list[Tile] = []
		duplicates: set[Tile] = set()
		for tile_index, tile in enumerate(sorted_tiles):
			for other_tile in sorted_tiles[tile_index + 1:]:
				if tile != other_tile\
					and (tile.box is not None)\
					and (other_tile.box is not None):
					if abs(other_tile.box.left - tile.box.left) < (PIXEL_EPSILON + 1)\
						and abs(other_tile.box.top - tile.box.top) < (PIXEL_EPSILON + 1)\
						and other_tile not in duplicates:
							duplicates.add(other_tile)
			tile_index += 1

		for tile in sorted_tiles:
			if tile not in duplicates:
				deduped_tiles.append(tile)

		y_sorted_tiles = sorted(deduped_tiles, key=lambda tile: tile.box.top // PIXEL_EPSILON if tile.box is not None else -1)
		tiles_in_y: list[Tile] = [y_sorted_tiles[0]]
		y_x_sorted_tiles: list[list[Tile]] = []
		for tile in y_sorted_tiles[1:]:
			if abs(tile.box.top - tiles_in_y[0].box.top) < (PIXEL_EPSILON + 1):
				tiles_in_y.append(tile)
			else:
				x_sorted_tiles = sorted(tiles_in_y, key=lambda tile: tile.box.left // PIXEL_EPSILON)
				y_x_sorted_tiles.append(x_sorted_tiles)
				tiles_in_y = [tile]

		x_sorted_tiles = sorted(tiles_in_y, key=lambda tile: tile.box.left // PIXEL_EPSILON)
		y_x_sorted_tiles.append(x_sorted_tiles)

		if len(deduped_tiles) != 61:
			raise ValueError("Unable to infer all tiles on the board!")

		tile_index = 0
		for row_index, row in enumerate(self.grid):
			for col_index, tile in enumerate(row):
				self.grid[row_index][col_index] = y_x_sorted_tiles[row_index][col_index]
				tile_index += 1

	def find_next_tile(self) -> Tile | None:
		for row in self.grid:
			for tile in row:
				if tile.kind != self.WIN_TILE_KIND:
					print(f"found non-winning tile:\n{tile}\n{tile.box}, {tile.kind}")
					neighbors = self.get_neighboring_tiles(center_tile=tile)
					if neighbors[-1]:
						return neighbors[-1]
		if self.is_solved():
			print("Time to start solving this terminal!")
			self.solve_terminal()
			return self.find_next_tile()
		else:
			print("Solved!")
			return None

	def get_neighboring_tiles(self, center_tile: Tile) -> list[Tile | None]:
		(x, y) = self.get_tile_coordinates(center_tile)
		neighbors: list[Tile | None] = []
		top_half_directions = ((-1, -1), (0, -1), (-1, 0), (1, 0), (0, 1), (1, 1))
		middle_directions = ((-1, -1), (0, -1), (-1, 0), (1, 0), (-1, 1), (0, 1))
		bottom_half_directions = ((0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1))
		directions: tuple[tuple[int, int], ...] = ()
		if y < 4:
			directions = top_half_directions
		elif y == 4:
			directions = middle_directions
		elif y > 4:
			directions = bottom_half_directions
		for [x_delta, y_delta] in directions:
			(neighbor_x, neighbor_y) = (x + x_delta, y + y_delta)
			if 0 <= neighbor_y and neighbor_y < len(self.grid)\
				and 0 <= neighbor_x and neighbor_x < len(self.grid[neighbor_y]):
					neighbor = self.grid[neighbor_y][neighbor_x]
					neighbors.append(neighbor)
			else:
				neighbors.append(None)
		return neighbors

	def solve_terminal(self):
		terminal_row = [
			1 if self.grid[8][0].kind == self.WIN_TILE_KIND else 0,
			1 if self.grid[8][1].kind == self.WIN_TILE_KIND else 0,
			1 if self.grid[8][2].kind == self.WIN_TILE_KIND else 0,
			1 if self.grid[8][3].kind == self.WIN_TILE_KIND else 0,
			1 if self.grid[8][4].kind == self.WIN_TILE_KIND else 0,
			1 if self.grid[7][5].kind == self.WIN_TILE_KIND else 0,
			1 if self.grid[6][6].kind == self.WIN_TILE_KIND else 0,
			1 if self.grid[5][7].kind == self.WIN_TILE_KIND else 0,
			1 if self.grid[4][8].kind == self.WIN_TILE_KIND else 0,
		]

		testing_rows = [[0 for _ in range(9)] for __ in range(9)]

		for y, testing_row in enumerate(testing_rows):
			if terminal_row[y] == 1:
				for x, _ in enumerate(testing_row):
					testing_row[x] = TERMINAL_BOARD_PATTERNS[y][x]

		solution_row = [0 for _ in range(9)]
		for x, _ in enumerate(solution_row):
			row_sum = 0
			for testing_row in testing_rows:
				row_sum += testing_row[x]
			if row_sum % 2 != 0:
				solution_row[x] = 1

		beginning_row = [
			self.grid[4][0],
			self.grid[3][0],
			self.grid[2][0],
			self.grid[1][0],
			self.grid[0][0],
			self.grid[0][1],
			self.grid[0][2],
			self.grid[0][3],
			self.grid[0][4]
		]

		tiles_to_click: list[Tile] = []
		for x, testing_row in enumerate(solution_row):
			if testing_row == 1:
				tile_to_click = beginning_row[x]
				tiles_to_click.append(tile_to_click)

		for tile in tiles_to_click:
			self.click_tile(tile)

	def get_tile_coordinates(self, tile: Tile) -> tuple[int, int]:
		for y, row in enumerate(self.grid):
			for x, tile in enumerate(row):
				if self.grid[y][x] == tile:
					return (x, y)
		raise ValueError(f"unable to get tile coordinates for tile:{tile}")

	def click_tile(self, tile: Tile):
		delay = CLICK_DELAY
		if BAN_EVASION_MODE:
			delay += random.uniform(0, DELAY_FUZZING)
		time.sleep(delay)
		if tile.box is None:
			raise ValueError("Require a box to click.")
		center = pyautogui.center(tile.box)
		if BAN_EVASION_MODE:
			center = (
				center[0] + random.randint(-HOVER_FUZZING[0], HOVER_FUZZING[0]), 
				center[1] + random.randint(-HOVER_FUZZING[1], HOVER_FUZZING[1])
			)
		print(f"center: {center}")
		pyautogui.click(center[0], center[1])
		neighbors: list[Tile | None] = self.get_neighboring_tiles(tile)
		neighbors.append(tile)
		for neighbor in neighbors:
			if neighbor is None or neighbor.kind is TileKind.UNKNOWN:
				continue
			elif neighbor.kind == TileKind.GLOOM:
				neighbor.kind = TileKind.GLIMMER
			elif neighbor.kind == TileKind.GLIMMER:
				neighbor.kind = TileKind.GLOOM
		# pyautogui.moveTo(MOUSE_EXIT_BOX[0] + 10, MOUSE_EXIT_BOX[1] + 10)
		(x, y) = self.get_tile_coordinates(tile)
		print(f"clicked tile: {tile.box}, {tile.kind}\ngrid[{y}][{x}]\n{self}")

def solve_board():
	game_board = GameBoard()
	move_counter = 0
	while(not game_board.is_solved()):
		if move_counter % 7 == 0:
			game_board = GameBoard()
		print(f"game board:\n{game_board}")
		next_tile = game_board.find_next_tile()
		if next_tile is not None and next_tile.box is not None:
			print(f"clicking next tile:\n{next_tile}")
			game_board.click_tile(next_tile)
		if keyboard.is_pressed(END_SCRIPT_KEY):
			print("Key press detected! Aborting script...")
			break
		move_counter += 1
	return

if __name__ == "__main__":
	solve_board()
