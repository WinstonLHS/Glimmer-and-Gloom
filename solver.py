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
		self.solving_terminal = False
		self.is_solved = False
		self.find_all()

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
		raw_inferred_tiles: list[Tile] = []
		for box in pyautogui.locateAllOnScreen("gloom.png", confidence=0.75):
			raw_inferred_tiles.append(Tile(TileKind.GLOOM, box))
		for box in pyautogui.locateAllOnScreen("glimmer.png", confidence=0.75):
			raw_inferred_tiles.append(Tile(TileKind.GLIMMER, box))

		sorted_inferred_tiles = sorted(raw_inferred_tiles, key=lambda tile: (tile.box.top, tile.box.left))

		new_tiles: list[Tile] = []
		duplicates: list[Tile] = []
		PIXEL_EPSILON: int = 5
		for tile_index, tile in enumerate(sorted_inferred_tiles):
			for _, other_tile in enumerate(sorted_inferred_tiles):
				if tile != other_tile and (tile.box is not None) and (other_tile.box is not None):
					if abs(other_tile.box.left - tile.box.left) < PIXEL_EPSILON\
						and abs(other_tile.box.top - tile.box.top) < PIXEL_EPSILON\
						and other_tile not in duplicates:
							duplicates.append(other_tile)

			if tile not in duplicates:
				new_tiles.append(tile)
			tile_index += 1


		new_rows: list[list[Tile]] = []
		last_box_top = -999
		new_row: list[Tile] = []
		for tile in new_tiles:
			if abs(last_box_top - tile.box.top) < PIXEL_EPSILON:
				new_row.append(tile)
			else:
				new_rows.append(new_row)
				new_row = []

		for row_index, row in enumerate(new_rows):
			for col_index, tile in enumerate(row):
				self.grid[row_index][col_index] = tile

	def find_next_tile(self) -> Tile | None:
		for _, row in enumerate(self.grid):
			for __, tile in enumerate(row):
				if tile.kind is TileKind.GLIMMER:
					print(f"found glimmer: {tile}")
					neighbors = self.get_neighboring_tiles(tile=tile)
					if neighbors[5]:
						return neighbors[5]
		if self.solving_terminal is False:
			print("Time to start solving this terminal!")
			self.solve_terminal()
			self.solving_terminal = True
			return self.find_next_tile()
		else:
			print("Solved!")
			self.is_solved = True
			return None

	def get_neighboring_tiles(self, tile: Tile) -> list[Tile]:
		[x, y] = self.get_tile_coordinates(tile)
		neighbors: list[Tile] = []
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
			if neighbor_y in range(0, len(self.grid)):
				if neighbor_x in range(0, len(self.grid[neighbor_y])):
					neighbors.append(
						self.grid[neighbor_y][neighbor_x]
					)
			# 	else:
			# 		neighbors.append(Tile())
			# else:
			# 	neighbors.append(Tile())
		return neighbors

	def solve_terminal(self):
		WIN_TILE_KIND = TileKind.GLIMMER
		terminal_row = (
			1 if self.grid[8][0].kind == WIN_TILE_KIND else 0,
			1 if self.grid[8][1].kind == WIN_TILE_KIND else 0,
			1 if self.grid[8][2].kind == WIN_TILE_KIND else 0,
			1 if self.grid[8][3].kind == WIN_TILE_KIND else 0,
			1 if self.grid[8][4].kind == WIN_TILE_KIND else 0,
			1 if self.grid[7][5].kind == WIN_TILE_KIND else 0,
			1 if self.grid[6][6].kind == WIN_TILE_KIND else 0,
			1 if self.grid[5][7].kind == WIN_TILE_KIND else 0,
			1 if self.grid[4][8].kind == WIN_TILE_KIND else 0,
		)

		testing_rows = [[0 for _ in range(9)] for __ in range(9)]

		for y, row in enumerate(testing_rows):
			compare = terminal_row[y]
			if compare == 1:
				for x, tile in enumerate(row):
					row[x] = TERMINAL_BOARD_PATTERNS[y][x]

		solution_row = [0 for _ in range(9)]
		for x in range(len(solution_row)):
			one_sum = 0
			for row in testing_rows:
				one_sum += row[x]
			if one_sum % 2 != 0:
				solution_row[x] = 1

		beginning_row = (
			self.grid[4][0],
			self.grid[3][0],
			self.grid[2][0],
			self.grid[1][0],
			self.grid[0][0],
			self.grid[0][1],
			self.grid[0][2],
			self.grid[0][3],
			self.grid[0][4]
		)

		tiles_to_click: list[Tile] = []
		for x in range(len(solution_row)):
			if solution_row[x] == 1:
				print(f'solution row is {solution_row} and beginning_row is {beginning_row}')
				tiles_to_click.append(beginning_row[x])

		for tile in tiles_to_click:
			self.click_tile(tile)

	def get_tile_coordinates(self, tile: Tile) -> tuple[int, int]:
		for y, row in enumerate(self.grid):
			for x, tile in enumerate(row):
				if self.grid[y][x] == tile:
					return (x, y)
		raise ValueError(f"unable to get tile coordinates for tile:{tile}")

	def click_tile(self, tile: Tile):
		print("Clicking tile:")
		print(tile)
		delay = CLICK_DELAY
		if BAN_EVASION_MODE:
			delay += random.uniform(0, DELAY_FUZZING)
		time.sleep(delay)
		if tile.box is None:
			raise ValueError
		center = pyautogui.center(tile.box)
		if BAN_EVASION_MODE:
			center = (
				center[0] + random.randint(-HOVER_FUZZING[0], HOVER_FUZZING[0]), 
				center[1] + random.randint(-HOVER_FUZZING[1], HOVER_FUZZING[1])
			)
		print(center)
		pyautogui.click(center[0], center[1])
		neighbors: list[Tile] = self.get_neighboring_tiles(tile)
		neighbors.append(tile)
		for neighbor in neighbors:
			if neighbor.kind is TileKind.UNKNOWN:
				continue
			elif neighbor.kind == TileKind.GLOOM:
				neighbor.kind = TileKind.GLIMMER
			elif neighbor.kind == TileKind.GLIMMER:
				neighbor.kind = TileKind.GLOOM
		# pyautogui.moveTo(MOUSE_EXIT_BOX[0] + 10, MOUSE_EXIT_BOX[1] + 10)
		print(self)

def solve_board():
	game_board = GameBoard()
	game_board_printed = str(game_board)
	print(game_board_printed)
	move_count = 0
	while(not game_board.is_solved):
		move_count += 1
		# if move_count % 7 == 0:
		# 	game_board = GameBoard()
		game_board_printed = str(game_board)
		print(game_board_printed)
		next_tile = game_board.find_next_tile()
		print(next_tile)
		if next_tile is not None:
			game_board.click_tile(next_tile)
		if keyboard.is_pressed(END_SCRIPT_KEY):
			print("Key press detected! Aborting script...")
			break
	return

if __name__ == "__main__":
	solve_board()
