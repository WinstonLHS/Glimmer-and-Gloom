# Plays indefinitely.

import pyautogui
import time
import keyboard
from solver import *
from variables import *

def autorun():
	n = 0 # DO NOT CHANGE THIS!!!!
	print("Starting the game, we'll play " + str(NUM_LOOPS) + " rounds.")
	while n <= NUM_LOOPS:
		n += 1
		try:
			print("Beginning round #" + str(n) + "...")
			solve_board()
			time.sleep(GAME_DELAY)
			pyautogui.click(
				pyautogui.center(
					pyautogui.locateOnScreen("play.png", confidence=0.75)
				)
			)
			time.sleep(GAME_DELAY)
			print("Ending round #" + str(n) + "...")
		except Exception as e:
			print(f'some exception occurred: {e}')
		if keyboard.is_pressed(END_SCRIPT_KEY):
			print("Key press detected! Aborting script...")
			break
	print("Exiting Script.")
