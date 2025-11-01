PLAY_FILE_LOC = "play.png" # The local file location of the play button image
GAME_DELAY = 1.54 # How much we wait before starting a new game.
NUM_LOOPS = 100 # The maximum number of games we'll play. After this number, the script will quit.

CLICK_DELAY = .1 # How much our default delay is before the next click is made.

BAN_EVASION_MODE = True # If set to True, waits a little and moves the mouse a little to evade suspicion. If set to False, we're just being efficient.
DELAY_FUZZING = .5 # The maximum amount of time we can delay a click.
HOVER_FUZZING = (8, 8) # The maximum (and negative minumum) we can alter the mouse click position by.

END_SCRIPT_KEY = "q" # Use this to quit the script immediately. HOLD the key, NOT spam it.
MOUSE_EXIT_BOX = (2, 2) # Where we bring the mouse near to allow for an easy quit out.

TERMINAL_BOARD_PATTERNS = (
	(0, 0, 0, 1, 0, 1, 0, 0, 1),
	(0, 0, 0, 0, 1, 1, 1, 1, 0),
	(0, 0, 1, 1, 0, 1, 0, 1, 0),
	(1, 0, 1, 1, 0, 1, 1, 1, 1),
	(0, 1, 0, 0, 1, 0, 0, 1, 0),
	(1, 1, 1, 1, 0, 1, 1, 0, 1),
	(0, 1, 0, 1, 0, 1, 1, 0, 0),
	(0, 1, 1, 1, 1, 0, 0, 0, 0),
	(1, 0, 0, 1, 0, 1, 0, 0, 0)
)
