from curses import initscr, noecho
from random import randint, choices
from os import system, popen, path
from time import sleep, time
from threading import Thread
from sys import exit, argv

################################################################################################
###########################################################-- Useful Variables --###############
################################################################################################
lives = 		5	# starting level lives
BEAST_SCR = 	6	# points for killing beasts
EGG_SCR = 		8	# points for killing eggs
MONSTER_SCR =	10	# points for killing monsters
NO_LIVES = 		50	# point penalty for losing all lives
NO_LEVEL = 		3	# level penalty for losing all lives
WIN_LEVEL =		25	# points for winning a level
PLR_FLASHES = 	7	# Number of times a spawned player flashes
SCENT = 		20	# distance at which enemies smell you strongly
SCENT_EDGE = 	20	# distance past scent for mild scent
#########################################################-- pawn speeds
beast_steps = 	4	# (1 - 10), higher is slower
monster_steps =	3	# (1 - 10), higher is slower
incubation = 	8	# (1 - 10), higher is slower
egg_timer = 	7	# (1 - 10), higher is slower
#########################################################-- game frame time
LCD_TIME = 		.02	# example: .02 = 1 frame every .02 seconds = 2/100 >>> 100/2 fps = 50 fps
#########################################################-- size of the board
# Lowest possible values are 15 x 30. Old game was 20 x 40.
play_rows = 	20	# 15+ Height
play_cols = 	40	# 30+ Width
#########################################################-- game levels
# You can create as many or few levels as you want to here.
# Each level is surrounded by curly brackets, while the outer brackets are square
# Make sure all bracketted levels are followed by a comma (except for the last level)
# Blocks and Boxes:
#	> Negative Integer: use built-in count formula
#		> The default formula stays within a pretty small range.
#	> Positive Integer: specify exact number of blocks or boxes
#	> Negative decimal: subtracts percentage of blocks/boxes from default formula
#		> ie: -.15 (has absolute value less than 1)
#	> Positive decimal: adds percentage of blocks/boxes to default formula
#		> ie: .15 (has absolute value less than 1)
GAME_LEVELS = [
		{'beasts':3,	'monsters':0,	'eggs':0, 	'block': 'yellow',	'blocks': -999,	'boxes': -999},	# Level 1
		{'beasts':5,	'monsters':0,	'eggs':0,	'block': 'orange',	'blocks': -999,	'boxes': -999},	# Level 2
		{'beasts':5,	'monsters':0,	'eggs':2,	'block': 'yellow',	'blocks': -999,	'boxes': -999},	# Level 3
		{'beasts':1,	'monsters':1,	'eggs':3,	'block': 'orange',	'blocks': -999,	'boxes': -999},	# Level 4
		{'beasts':4,	'monsters':2,	'eggs':2,	'block': 'yellow',	'blocks': -999,	'boxes': -999},	# Level 5
		{'beasts':8,	'monsters':0,	'eggs':0,	'block': 'orange',	'blocks': -999,	'boxes': 47},	# Level 6
		{'beasts':0,	'monsters':0,	'eggs':8,	'block': 'orange',	'blocks': -999,	'boxes': 47},	# Level 7
		{'beasts':0,	'monsters':8,	'eggs':0,	'block': 'orange',	'blocks': -999,	'boxes': 47},	# Level 8
		{'beasts':3,	'monsters':3,	'eggs':3,	'block': 'yellow',	'blocks': -999,	'boxes': -999},	# Level 9
		{'beasts':2,	'monsters':4,	'eggs':3,	'block': 'yellow',	'blocks': -999,	'boxes': -999},	# Level 10
		{'beasts':1,	'monsters':5,	'eggs':4,	'block': 'orange',	'blocks': -999,	'boxes': -999},	# Level 11
		{'beasts':1,	'monsters':6,	'eggs':4,	'block': 'orange',	'blocks': -999,	'boxes': -999},	# Level 12
		{'beasts':0,	'monsters':0,	'eggs':12,	'block': 'yellow',	'blocks': -999,	'boxes': -999},	# Level 13
		{'beasts':0,	'monsters':12,	'eggs':0,	'block': 'orange',	'blocks': -999,	'boxes': -999},	# Level 14
		{'beasts':15,	'monsters':0,	'eggs':0,	'block': 'orange',	'blocks': -999,	'boxes': -999} 	# Level 15
	]
lowest_boxes = 15 # Some boxes are required to play the game
########################################################-- Pawn Movement Priority Odds
# These values are the odds of moves for an enemy if those		|---------------------
# moves are available to it. If a move is not available,		| 5  4  3
# then its odds are absorbed: 1st by its equal counterpart,		| 4  H  2
# and then by the next lower priority, etc. Each of the 5 		| 3  2  1
# priorities is greater or equal to the sum of all lower 		|		 \
# priority moves' odds.											|	      \
########################-- Examples								|		   <>
# Max Randomness	1, 1, 1, 3, 3, 9, 9, 27
# High				1, 1, 1, 4, 4, 16, 16, 50		1, 2, 2, 6, 6, 18, 18, 55
# Medium			1, 1, 1, 4, 4, 20, 20, 90		1, 2, 2, 8, 8, 26, 26, 98
# Low Randomness	1, 3, 3, 12, 12, 40, 40, 200

PRIORITY_ODDS = [
		[98, False],	# Forward (1st priority)
		[28, False],	# Front-Side (2nd priority)
		[28, False],	# Front-Side (2nd priority)
		[4, False],		# Sideways (3rd priority)
		[4, False],		# Sideways (3rd priority)
		[1, False],		# Rear-Side (4th priority)
		[1, False],		# Rear-Side (4th priority)
		[1, False] 		# Backwards (5th priority)
	]
#####################################################-- player direction controls
# Without editing, the default settings option is the middle one.
# The script only allows for a total of 3 options at a time
# Customize the 3 options below with key codes from getkeycodes, as well as custom titles.
# Changing the value of word as in ............ "title":"word"
#	> changes the script -k option to: ........ -k:word
#	> changes the settings menu option to: .... [ word ]

KYBD = [
		{"title":"wasd", "K_UP":119, "K_DOWN":115, "K_RIGHT":100, "K_LEFT":97,  "PK_UP":87,  "PK_DOWN":83,  "PK_RIGHT":68,  "PK_LEFT":65},
		#{"title":"XBOX",  "K_UP":105, "K_DOWN":117, "K_RIGHT":111, "K_LEFT":121, "PK_UP":73, "PK_DOWN":85, "PK_RIGHT":79, "PK_LEFT":89},
		{"title":"arrows",  "K_UP":259, "K_DOWN":258, "K_RIGHT":261, "K_LEFT":260, "PK_UP":337, "PK_DOWN":336, "PK_RIGHT":402, "PK_LEFT":393},
		{"title":"hjkl", "K_UP":107, "K_DOWN":106, "K_RIGHT":108, "K_LEFT":104, "PK_UP":75,  "PK_DOWN":74,  "PK_RIGHT":76,  "PK_LEFT":72}
	]
################################################################################################
###########################################################-- Utility Functions --##############
################################################################################################
######################################-- Linux aplay audio function
def play_audio(filename): system('aplay -q ' + script_dir + '/audio/' + filename + '.wav &')
script_dir = path.abspath( path.dirname( __file__ ) )
play_audio('menu_item_tick') # Sound test helps "initialize" in some cases
######################################-- get terminal size
def get_rw_cl_tcl(rw, cl, tcl): # get rows, columns, and terminal columns
	rows, ttycols = [int(x) for x in popen('stty size', 'r').read().split()]
	size = []
	if int(rw): size.append(rows)
	if int(cl): size.append(int(ttycols / 2))
	if int(tcl): size.append(ttycols)
	if len(size) == 1: return size[0]
	else: return size
term_rows, term_cols = get_rw_cl_tcl(1,0,1) # variables track changing terminal size
#########################################################-- background color ansi
def tbg(rtrn): # tbg(1)
	global xbgx, trnsprnt
	if trnsprnt: xbgx = '\033[49m'
	else: xbgx = '\033[40m'
	if rtrn == 1: return xbgx
xbgx = '\033[40m'
trnsprnt = False
################################################################################################
######################################################-- More Global Variables --###############
################################################################################################
dir_keys = 1	# default key controls is the center option
left_pad = 0	# padding for terminal fitted screen
top_pad = 0		# padding for terminal fitted screen
fitted = False	# whether or not the -f option is chosen
stat_rows = 1	# rows for game stats
################################################-- argv assignments
for i in argv:
	if i[0:3] == '-f:':
		if(i[3:].isdigit() and len(i[3:]) < 3):
			left_pad = int(i[3:]) * 2
			top_pad = int(i[3:])
		else:
			left_pad = 0
			top_pad = 0
	else:
		left_pad = 0
		top_pad = 0
	if i[0:2] == '-f':
		fitted = True
		term_rows, tot_cols = get_rw_cl_tcl(1,0,1)
		if term_rows % 2 == 0: alt = 0
		else: alt = 1
		play_rows = term_rows - 2 - top_pad*2 - stat_rows
		play_cols = (tot_cols - 4 - left_pad * 2) / 2

for i in argv:
	if i[0:2] == '-t':
		xbgx = '\033[49m'
		trnsprnt = True
	if i[0:3] == '-k:':	# "wasd", "arrows", "hjkl"
		if i[3:] == KYBD[0]['title']: dir_keys = 0
		elif i[3:] == KYBD[1]['title']: dir_keys = 1
		elif i[3:] == KYBD[2]['title']: dir_keys = 2
	if i[0:3] == '-h:':
		if(i[3:].isdigit() and len(i[3:]) < 121):
			play_rows = int(i[3:]) + top_pad*2
	if i[0:3] == '-w:':
		if(i[3:].isdigit() and len(i[3:]) < 121):
			play_cols = int(i[3:]) + left_pad
################################################-- keyboard constants post argv
KEY_UP = 		KYBD[dir_keys]["K_UP"]
KEY_DOWN = 		KYBD[dir_keys]["K_DOWN"]
KEY_RIGHT = 	KYBD[dir_keys]["K_RIGHT"]
KEY_LEFT = 		KYBD[dir_keys]["K_LEFT"]
KEY_P_UP = 		KYBD[dir_keys]["PK_UP"]
KEY_P_DOWN = 	KYBD[dir_keys]["PK_DOWN"]
KEY_P_RIGHT = 	KYBD[dir_keys]["PK_RIGHT"]
KEY_P_LEFT = 	KYBD[dir_keys]["PK_LEFT"]
################################################-- other game variables
#fps_avg_frames = LCD_TIME
mi1_opt = dir_keys + 1 # initial keyboard setting
keypress = 999
debug = False
pulling = 'hold' # 'hold / 'tog' /  'swi' / 'sin'
game_play_mode = False
################################################-- set background post argv
tbg(0) # set xbgx after argv, and before character contants
################################################-- formatted character constants
# 			Foreground	+  Background	+    	Unicode Chars		+ 	Reset
BAKGRD =				  xbgx 			+ '  '
BLOCK =					  '\033[43m'	+ '  '						+ '\033[0m'
KILLBLOCK =	'\033[31m'	+ '\033[43m'	+ chr(9618) + chr(9618) 	+ '\033[0m'
BOX =		'\033[32m'	+ xbgx 			+ chr(9618) + chr(9618) 	+ '\033[0m'
BEAST =		'\033[31m'	+ xbgx 			+ chr(9500) + chr(9508) 	+ '\033[0m'
MONSTER =	'\033[31m'	+ xbgx 			+ chr(9568) + chr(9571) 	+ '\033[0m'
PLAYER =	'\033[34m'	+ xbgx 			+ chr(9664) + chr(9654) 	+ '\033[0m'
# https://en.wikipedia.org/wiki/ANSI_escape_code
eggsub = 8329   # unicode key for subscript 9 (8328 = 8, and so on)
egg2nd = 32     # unicode key for a space character
# The below function returns and egg character with the appropriate subscript
def EGG(sub):
	return '\033[0m\033[0m\033[0m\033[37m' + xbgx + '\033[2m' + chr(11052) + '\033[1m' + chr(sub) + '\033[0m'
# The below function is used to detect an egg independent of its changing subscript
def deteggt(chegg):
	if (chegg[0:12] == '\033[0m\033[0m\033[0m'): return True
################################################-- adapt speed variables
beast_speed = 	.5 + .2 * (beast_steps - 1)
monster_speed =	.5 + .2 * (monster_steps - 1)
incubate = 		 4 +  4 * (incubation - 1)
egg_speed = 	.5 + .5 * (egg_timer - 1)
################################################-- Pawn Classes (Dictionaries)
beasts = 	[{ 'frames': 		(int(beast_speed / LCD_TIME)), 		'frame':0, 	'chr': BEAST, 'pnts': BEAST_SCR }]
monsters = 	[{ 'frames': 		(int(monster_speed / LCD_TIME)), 	'frame':0, 	'chr': MONSTER, 'pnts': MONSTER_SCR }]
eggs = 		[{ 'frames': 		(int(egg_speed / LCD_TIME)), 		'frame':0, 'incu_frames': (int(1 / LCD_TIME)), 'incu_frame': 0, 'pnts': EGG_SCR }]
player = 	[{ 'flash_frames': 	(int(.05 / LCD_TIME) * 2), 						'chr': PLAYER, 'pnts': 10 }]

PLR_FLASHES = (PLR_FLASHES * 2) + 1
plr_flash = 0
plr_frames = (int(.05 / LCD_TIME) * 2)
plr_frame = 0
################################################-- move constants
MOVES = {
	 'U': {	'ra':-1,	'ca':0	},	# ra - "row adjustment"
	 'D': {	'ra':1, 	'ca':0	},	# ca - "column adjustment"
	 'L': {	'ra':0, 	'ca':-1	},
	 'R': {	'ra':0, 	'ca':1	},
	'UL': {	'ra':-1, 	'ca':-1	},
	'UR': {	'ra':-1, 	'ca':1	},
	'DL': {	'ra':1, 	'ca':-1	},
	'DR': {	'ra':1, 	'ca':1	}
}
################################################-- board variables
level = 0
board = []
blank_board = []
if (play_rows < 15): play_rows = 15
if (play_cols < 30): play_cols = 30
play_rows = int(play_rows)
play_cols = int(play_cols)
board_rows = play_rows + 2
board_cols = play_cols + 2
lvl_box_cnt = 0
################################################-- spacing variables
left_margin = 0
top_margin = 0 # 1 is the lowest that the top margin can be, because of a specific issue with the print function
stat_grow_limit = 52 # greatest board width of centered stats
left_stat = 6
min_rows = board_rows + stat_rows
################################################################################################
###########################################################-- Utility Functions --##############
################################################################################################
def close_game(): # close game function
	system('clear')
	print('\033[?25\033[0;0H')
	try:
		raise KeyboardInterrupt
	except KeyboardInterrupt:
		print('\033[?25\033[0;0H')
		system('clear')
		system('reset')
	finally:
		print('\033[?25\033[0;0H')
		system('clear')
		system('reset')
		exit(0)
########################################################-- cursor preset functions
def set_topleft(top, left):
	global top_margin, left_margin, xbgx
	tbg(0)
	print('\033[?25l\033[?7l\033[' + str(2 + top_margin + top)  + ';' + str(4 + left_margin + left) + 'H\033[s\033[0m' + xbgx)

def set_botleft(bottom, left):
	global top_margin, left_margin, board_cols, board_rows, xbgx
	print('\033[?25l\033[?7l\033[' + str(top_margin + int(board_rows - bottom - 3)) + ';' + str(4 + left_margin + left) + 'H\033[s\033[0m' + xbgx)

#def set_topcent(top, leftcomp):
#	global top_margin, left_margin, board_cols
#	print('\033[?25l\033[' + str(2 + top_margin + top) + ';' + str(left_margin + int(board_cols) - leftcomp) + 'H\033[s\033[0m')

def set_midcent(topcomp, leftcomp):
	global top_margin, left_margin, board_cols, board_rows, xbgx
	print('\033[?25l\033[?7l\033[' + str(top_margin + int(board_rows / 2) - topcomp) + ';' + str(left_margin + board_cols - leftcomp) + 'H\033[s\033[0m' + xbgx)
################################################################################################
###########################################################-- Board Functions --################
################################################################################################
######################################-- get/set game dimensions
def set_board_spacing(): #{
	global top_margin, left_margin, board_rows, board_cols, play_rows, play_cols, term_cols, term_rows
	global left_stat, statpad, stat_rows, min_rows, stat_grow_limit, level, debug, keypress

	if (board_rows > term_rows - 6):
		debug = False

	if (debug):
		top_margin = 0
		left_margin = 0
	else:
		left_margin = int((term_cols - (board_cols*2)) / 2)
		top_margin = int((term_rows - min_rows) / 2)

	left_margin += 1
	top_margin += 1

	if board_cols <= stat_grow_limit:
		statpad = left_stat
	else:
		statpad = board_cols - stat_grow_limit + left_stat

######################################-- Create new board array with background and border
def build_the_board(): #{ BUILDS a blank board
	global board_cols, board_rows

	screen_board = []

	for rowi in range(board_rows): # builds the board based on 'board_rows' and 'board_cols' which includes room for borders
		screen_board.append([])
		for coli in range(board_cols):
			screen_board[rowi].append([])
			screen_board[rowi][coli] = BAKGRD

	for rowi in range(board_rows): # draws the game boarders on the board
		for coli in range(board_cols):
			if(rowi == 0) or (rowi == (board_rows - 1)) or (coli == 0) or (coli == (board_cols - 1)):
				screen_board[rowi][coli] = BLOCK

	return screen_board
#}

def print_stats():
	global top_margin, left_margin, score, lives, level, board_rows, board_cols, statpad, play_rows, play_cols, term_cols, term_rows
	level_stat = chr(9477) + ' LEVEL: ' + str(level) + ' ' + chr(9477)
	score_stat = chr(9477) + ' SCORE: ' + str(score) + ' ' + chr(9477)
	lives_stat = chr(9477) + ' LIVES: ' + str(lives) + ' ' + chr(9477)

	print('\033[?7l\033[' + str(top_margin + board_rows) + ';' + str(left_margin) + 'H\033[s\033[0m\033[37m' +
		'\033[s\033[' + str(statpad) 									+ 'C'	+ level_stat + '   ' +
		'\033[u\033[' + str(board_cols - int(len(score_stat)/2))		+ 'C' 	+ score_stat + '   ' +
		'\033[u\033[' + str(board_cols*2 - statpad - len(lives_stat))	+ 'C' 	+ lives_stat + '   ' + '\033[1A')

def print_debug():
	global top_margin, left_margin, score, lives, level, board_rows, board_cols, statpad, play_rows, play_cols, term_cols, term_rows
	print('\033[?7l\033[1;1H\033[' + str(top_margin + board_rows + 2) + ';' + str(left_margin) + 'H\033[s\033[0m\033[37m' +
	'Player: ' + str(player) )
	for i in range(0, len(eggs)):
		if i == 0: print('\033[u' + '\033[' + str(2 + i) + 'B' + '\r\033[K\033[1B\033[K\033[?7l\033[1A\033[0m\033[37mEggs: ' + str(eggs[i]))
		else: print('\033[u' + '\033[' + str(2 + i) + 'B' + '\r\033[K\033[1B\033[K\033[?7l\033[1A\t\033[0m\033[37mEgg ' + str(i) + ': ' + str(eggs[i]))
	for i in range(0, len(beasts)):
		if i == 0: print('\033[u' + '\033[' + str(len(eggs) + 3 + i) + 'B' + '\r\033[K\033[1B\033[K\033[?7l\033[1A\033[0m\033[37mBeasts: ' + str(beasts[i]))
		else: print('\033[u' + '\033[' + str(len(eggs) + 3 + i) + 'B' + '\r\033[K\033[1B\033[K\033[?7l\033[1A\t\033[0m\033[37mBeast ' + str(i) + ': ' + str(beasts[i]))
	for i in range(0, len(monsters)):
		if i == 0: print('\033[u' + '\033[' + str(len(eggs) + len(beasts) + 4 + i) + 'B' + '\r\033[K\033[?7l\033[1B\033[K\033[1A\033[0m\033[37mMonsters: ' + str(monsters[i]))
		else: print('\033[u' + '\033[' + str(len(eggs) + len(beasts) + 4 + i) + 'B' + '\r\033[K\033[?7l\033[1B\033[K\033[1A\t\033[0m\033[37mMonster ' + str(i) + ': ' + str(monsters[i]))

def egg_debug():
	global top_margin, left_margin, score, lives, level, board_rows, board_cols, statpad, play_rows, play_cols, term_cols, term_rows
	print('\033[?25\033[?7l\033[' + str(top_margin + board_rows + 1) + ';' + str(left_margin) + 'H\033[s\033[0m\033[37mEggs: ')
	for i in range(1, len(eggs)):
		if( ( player[1]['ro'] == eggs[i]['ro'] ) or ( player[1]['co'] == eggs[i]['co'] ) ):
			print('\033[u' + '\033[' + str(i) + 'B' + '\r\033[K\033[1B\033[K\033[?7l\033[1A\t\033[0m\033[37mEgg ' + str(i) + ':  Row:' + str(eggs[i]['ro']) + '  Col:' + str(eggs[i]['co']) )
		else:
			print('\033[u' + '\033[' + str(i) + 'B' + '\r\033[K\033[1B\033[K\033[?7l\033[1A\t\033[0m\033[37mEgg ' + str(i))

########################################################-- print board function
def print_board(board_array): #{
	global top_margin, left_margin, score, lives, level, board_rows, board_cols, statpad, play_rows, play_cols, term_cols, term_rows, keypress

	if(keypress == ord('r')):
		tot_rows, tot_cols = get_rw_cl_tcl(1,0,1)
		if (tot_rows != term_rows) or (tot_cols != term_cols):
			term_rows = tot_rows
			term_cols = tot_cols
			set_board_spacing()

	print('\033[0m\033[1;1H\033[?25l\033[?7l\033[' + str(top_margin) + ';' + str(left_margin) + 'H\033[s\033[0m\033[?7l')

	for rowi in range(board_rows):
		if (rowi == 0): print('\033[0m\033[u\033[?7l' + ''.join(board_array[rowi]))
		else: print('\033[0m\033[u\033[?7l\033[' + str(rowi) +  'B' + ''.join(board_array[rowi]))

	if level > 0: print_stats()

	if debug: print_debug()
	#if debug: egg_debug()



##########################################-- place the pieces
def place_beasts(count):
	global beasts, board, BAKGRD, beast_speed, LCD_TIME

	beasts[0]['frames'] = (int(beast_speed / LCD_TIME))
	step = 0
	while(step < count):
		row = randint(1, (board_rows - 1))
		col = randint(1, (board_cols - 1))
		if(board[row][col] == BAKGRD):
			board[row][col] = BEAST
			beasts.append({'ro':row, 'co':col, 'stg':0 })
			step += 1
			beasts[step]['stg'] = randint(1, (beasts[0]['frames']))

def hatch_monster(row, col):
	global monsters, board, MONSTER, LCD_TIME, monster_speed

	monsters[0]['frames'] = (int(monster_speed / LCD_TIME))
	stagger = randint(1, (monsters[0]['frames']))
	board[row][col] = MONSTER
	monsters.append({'ro':row, 'co':col,'stg':stagger })

def place_monsters(count):
	global monsters, board, BAKGRD

	step = 0
	while(step < count):
		row = randint(1, (board_rows - 1))
		col = randint(1, (board_cols - 1))
		if(board[row][col] == BAKGRD):
			hatch_monster(row, col)
			step += 1
##################################################-- EGGS
def lay_egg(row, col):
	global incubate, monsters, beasts, eggs, board, egg_speed, LCD_TIME

	enemy_total = len(eggs) + len(beasts) + len(monsters)
	eggs[0]['frames'] = (int(egg_speed / LCD_TIME))
	wait_frames = int(eggs[0]['incu_frames'] * (( enemy_total * incubate ) / 10) + randint(0, (2 * eggs[0]['incu_frames']))) # seconds of wait time before egg starts counting down
	stag = randint(1, eggs[0]['frames']) # the frame that the egg counts down on
	board[row][col] = EGG(32)
	eggs.append({'ro': row, 'co': col, 'wait': wait_frames, 'stg': stag, 'sub':32})

def place_eggs(count):
	global board, BAKGRD

	step = 0
	while(step < count):
		row = randint(1, (board_rows - 1))
		col = randint(1, (board_cols - 1))
		if(board[row][col] == BAKGRD):
			lay_egg(row, col)
			step += 1

def hatch_eggs():
	# this function runs through all the eggs, and increments their time
	# it transition eggs from wait phase, to countdown, to Monster
	# wait_time is number of enemies at the time of creation times 4-16 (in seconds)
	# egg_speed is usually between 2 and 4 seconds. It is the time between countdown numbers
	global eggs, board, egg_speed, LCD_TIME, audio

	di = 0 # keeps track of index to accomodate for egg deletions

	if eggs[0]['frame'] >= eggs[0]['frames']:
		eggs[0]['frame'] = 0
	else:
		eggs[0]['frame'] += 1
	if eggs[0]['incu_frame'] >= eggs[0]['incu_frames']:
		eggs[0]['incu_frame'] = 0
	else:
		eggs[0]['incu_frame'] += 1
	# egg_speed, incu_frames, incu_frame, frames, frame, wait, stg
	# each egg: wait, stg
	for i in range(1, (len(eggs))):
		if (eggs[i - di]['wait'] > 0):
			eggs[i - di]['wait'] -= 1
		elif (eggs[i - di]['wait'] == 0) and (eggs[i - di]['sub'] == 32):
			eggs[i - di]['sub'] = 8329
		elif (eggs[i - di]['wait'] == 0) :
			if ((eggs[i - di]['stg'] == eggs[0]['frame']) and (eggs[i - di]['sub'] > 8320)):
				eggs[i - di]['sub'] -= 1
				board[eggs[i - di]['ro']][eggs[i - di]['co']] = EGG(eggs[i - di]['sub'])
			elif ((eggs[i - di]['sub'] == 8320) and (eggs[i - di]['stg'] == eggs[0]['frame'])):
				hatch_monster(eggs[i - di]['ro'], eggs[i - di]['co'])
				del eggs[i - di]
				play_audio('hatch')
				di += 1
#####################################-- move pieces
def flash_player():
	global player, PLAYER, PLR_FLASHES, plr_flash, plr_frames, plr_frame

	PLAYER_negative = '\033[0m\033[7m\033[34m' + xbgx + chr(9664) + chr(9654) + '\033[0m'

	if plr_flash <= PLR_FLASHES:
		if plr_frame < plr_frames:
			plr_frame += 1
		elif plr_frame == plr_frames:
			plr_frame = 0
			if board[player[1]['ro']][player[1]['co']] == PLAYER:
				board[player[1]['ro']][player[1]['co']] = PLAYER_negative
			else:
				board[player[1]['ro']][player[1]['co']] = PLAYER
			plr_flash += 1
	elif board[player[1]['ro']][player[1]['co']] == PLAYER_negative:
		board[player[1]['ro']][player[1]['co']] = PLAYER


def place_player():
	global player, PLAYER, plr_flash

	step = 0
	while(step < 1):
		row = randint(1, (board_rows - 1))
		col = randint(1, (board_cols - 1))
		if(board[row][col] == BAKGRD):
			board[row][col] = PLAYER
			step += 1
			player.append({'ro': row, 'co': col, 'tug': False })
			step += 1
	plr_flash = 0 # This is what induces the flash_player() functions

def kill_player():
	global BAKGRD, player, lives, board

	board[ player[1]['ro'] ][ player[1]['co'] ] = BAKGRD
	lives -= 1
	del player[1]
	if lives > 0:
		place_player()

	play_audio('death')

def move_enemies(pawns): #{
	global board, player, MOVES, PRIORITY_ODDS, PLR_FLASHES, plr_flash, SCENT, SCENT_EDGE

	if pawns[0]['frame'] >= pawns[0]['frames']:
		pawns[0]['frame'] = 0
	else:
		pawns[0]['frame'] += 1

	move_priority = []
	move = ''
	likely_moves = []

	for pwni in range(1, (len(pawns))): # in a given frame, loops through all pawns in a list if the pawn is staggered to move in the present frame, the pawn moves to a space
		if (pawns[pwni]['stg'] == pawns[0]['frame']):
			rdistance = player[1]['ro'] - pawns[pwni]['ro'] # player row minus beast row
			cdistance = player[1]['co'] - pawns[pwni]['co'] # player column minus beast column

			vdistance = int((cdistance**2 + rdistance**2)**.5) # distance equation

			if (rdistance == 0) or (cdistance == 0): # avoid division by zero
				distance_ratio = 0.0 # if the player is on the same row or column, the distance ratio is zero
			else:
				distance_ratio = rdistance / cdistance # division of row distance by column distance

			if ((rdistance < 0.0) and (cdistance < 0.0) and (distance_ratio >= .5) and (distance_ratio <= 2.0)):
				move_priority = [ 'UL', 'U', 'L', 'DL', 'UR', 'D', 'R', 'DR' ] # UPPER LEFT range priorities
			elif ((rdistance < 0.0) and (cdistance > 0.0) and (distance_ratio <= -.5) and (distance_ratio >= -2.0)):
				move_priority = [ 'UR', 'U', 'R', 'UL', 'DR', 'L', 'D', 'DL' ] # UPPER RIGHT range priorities
			elif ((rdistance > 0.0) and (cdistance > 0.0) and (distance_ratio >= .5) and (distance_ratio <= 2.0)):
				move_priority = [ 'DR', 'D', 'R', 'DL', 'UR', 'U', 'L', 'UL' ] # DOWN RIGHT range priorities
			elif ((rdistance > 0.0) and (cdistance < 0.0) and (distance_ratio <= -.5) and (distance_ratio >= -2.0)):
				move_priority = [ 'DL', 'D', 'L', 'UL', 'DR', 'U', 'R', 'UR' ] # DOWN LEFT range priorities
			elif ((rdistance < 0.0) and ((abs(distance_ratio) > 2.0) or (distance_ratio == 0.0))):
				move_priority = [ 'U', 'UL', 'UR', 'L', 'R', 'DL', 'DR', 'D' ] # UPWARD range priorities
			elif ((cdistance > 0.0) and ((abs(distance_ratio) < .5) or (distance_ratio == 0.0))):
				move_priority = [ 'R', 'UR', 'DR', 'U', 'D', 'UL', 'DL', 'L' ] # RIGHT range priorities
			elif ((rdistance > 0.0) and ((abs(distance_ratio) > 2.0) or (distance_ratio == 0.0))):
				move_priority = [ 'D', 'DL', 'DR', 'L', 'R', 'UL', 'UR', 'U' ] # DOWNWARD range priorities
			elif ((cdistance < 0.0) and ((abs(distance_ratio) < .5) or (distance_ratio == 0.0))):
				move_priority = [ 'L', 'UL', 'DL', 'U', 'D', 'UR', 'DR', 'R' ] # LEFT range priorities

			for priopti in range(8):
				# if the first priority move is the player, then take that move (pawn kills player)
				if ((board[ ((pawns[pwni]['ro']) + (MOVES[move_priority[0]]['ra'])) ][ ((pawns[pwni]['co']) + (MOVES[move_priority[0]]['ca'])) ]) == PLAYER ):
					if(plr_flash >= PLR_FLASHES): # player immunity while flashing
						move = move_priority[0]
						board[pawns[pwni]['ro']][pawns[pwni]['co']] = BAKGRD
						pawns[pwni]['ro'] = player[1]['ro']
						pawns[pwni]['co'] = player[1]['co']
						kill_player()
						board[pawns[pwni]['ro']][pawns[pwni]['co']] = pawns[0]['chr']
					return 0
				# else if the priority move is not available, then mark it as unavailable
				elif ((board[ ((pawns[pwni]['ro']) + (MOVES[move_priority[priopti]]['ra'])) ][ ((pawns[pwni]['co']) + (MOVES[move_priority[priopti]]['ca'])) ]) == BAKGRD ):
					PRIORITY_ODDS[priopti][1] = True
				else:
					PRIORITY_ODDS[priopti][1] = False
					if ((pawns[0]['chr'] == MONSTER) and ((board[ ((pawns[pwni]['ro']) + (MOVES[move_priority[0]]['ra'])) ][ ((pawns[pwni]['co']) + (MOVES[move_priority[0]]['ca'])) ] == MONSTER) or (board[ ((pawns[pwni]['ro']) + (MOVES[move_priority[0]]['ra'])) ][ ((pawns[pwni]['co']) + (MOVES[move_priority[0]]['ca'])) ] == BEAST))):
						if (choices([True, False], [3, 127], k=1)) == [True]:
							place_eggs(1)

			#######################################################################-- Add count of each available move to a list to create final odds

			if (vdistance <= SCENT): # if the player is within the strong scent range
				for prioddi in range(8): # loop through priorities to add them to likely_moves if available
					if (PRIORITY_ODDS[prioddi][1] == True): # if it is true that the priority move is a blank space, then loop through and fill out the likely_moves list
						for ti in range(PRIORITY_ODDS[prioddi][0]): # loop through by number in "priorities" loop, to fill out likely_moves list
							likely_moves.append(move_priority[prioddi])
					if ((prioddi == 2) or (prioddi == 4) or (prioddi == 6)):
						if ((not PRIORITY_ODDS[prioddi - 1][1]) and (PRIORITY_ODDS[prioddi][1] == True)):
							for ti in range(PRIORITY_ODDS[prioddi][0]):
								likely_moves.append(move_priority[prioddi])
			elif (vdistance > SCENT and vdistance <= SCENT+SCENT_EDGE): # If the player is in the mild scent range
				for prioddi in range(8):
					if (PRIORITY_ODDS[prioddi][1] == True):
						for i in range(8*5 - prioddi*3): # 24 -
							likely_moves.append(move_priority[prioddi])
			else: # If the player is outside range of enemy scent/smell(), then odds of all available moves is 1
				for prioddi in range(8):
					if (PRIORITY_ODDS[prioddi][1] == True):
						likely_moves.append(move_priority[prioddi])

			#######################################################################-- the move is finally decided out of the available set in the list
			if (len(likely_moves) > 0):
				move = likely_moves[randint(0, (len(likely_moves)) - 1)]
				likely_moves = []
				# pawn row plus move row adjustment
				# pawn col plus move col adjustment
				board[ pawns[pwni]['ro'] + MOVES[move]['ra'] ][ pawns[pwni]['co'] + MOVES[move]['ca'] ] = pawns[0]['chr']
				# pawn row and pawn col = bakgrd
				board[ pawns[pwni]['ro'] ][ pawns[pwni]['co'] ] = BAKGRD
				# pawn[pawni] row and col = new row and col
				pawns[pwni]['ro'] = pawns[pwni]['ro'] + MOVES[move]['ra']
				pawns[pwni]['co'] = pawns[pwni]['co'] + MOVES[move]['ca']
#}

def push_loop(intent):
	global player, eggs, board, BLOCK, MOVES, BAKGRD, BOX, PLAYER, lvl_box_cnt

	push_eggs = []

	stnce_r = player[1]['ro']
	stnce_c = player[1]['co']
	tug_r = stnce_r - MOVES[intent]['ra']
	tug_c = stnce_c - MOVES[intent]['ca']
	intend_r = stnce_r + MOVES[intent]['ra']
	intend_c = stnce_c + MOVES[intent]['ca']
	def probe_r(p_ind):
		return player[1]['ro'] + p_ind * MOVES[intent]['ra']
	def probe_c(p_ind):
		return player[1]['co'] + p_ind * MOVES[intent]['ca']
	def wall_r(p_ind):
		return player[1]['ro'] + (p_ind + 1) * MOVES[intent]['ra']
	def wall_c(p_ind):
		return player[1]['co'] + (p_ind + 1) * MOVES[intent]['ca']
	def ram_r(p_ind):
		return player[1]['ro'] + (p_ind - 1) * MOVES[intent]['ra']
	def ram_c(p_ind):
		return player[1]['co'] + (p_ind - 1) * MOVES[intent]['ca']

	def push_move():
		global BOX, BAKGRD, PLAYER, player

		for i in range(probe):
			board[ probe_r(probe - i) ][ probe_c(probe - i) ] = board[ probe_r(probe - 1 - i) ][ probe_c(probe - 1 - i) ]	# make board space same as preceeding space
		for i in range(len(push_eggs)):
			eggs[push_eggs[i]]['ro'] += MOVES[intent]['ra']
			eggs[push_eggs[i]]['co'] += MOVES[intent]['ca']
		if ((player[1]['tug']) and (board[tug_r][tug_c] == BOX)):
			board[tug_r][tug_c] = BAKGRD
			board[stnce_r][stnce_c] = BOX
		else:
			board[ player[1]['ro'] ][ player[1]['co'] ] = BAKGRD
		player[1]['ro'] = intend_r
		player[1]['co'] = intend_c								# make player fol and fow the player
		board[intend_r][intend_c] = PLAYER						# move_player()

	def kill_enemy(pawns, row, col):
		global score, board

		del_index = 0

		for i in range(1, (len(pawns))):
			if ((pawns[i]['ro'] == row) and (pawns[i]['co'] == col)):
				del_index = i
				break
		del pawns[del_index]
		score += pawns[0]['pnts']

	probe = 2
	loop = True
	while (loop):
		space = board[probe_r(probe)][probe_c(probe)]

		if (((probe_r(probe) != 0) and (probe_r(probe) != (len(board) - 1))) and ((probe_c(probe) != 0) and (probe_c(probe) != len(board[0]) - 1))):
			wall_space = board[wall_r(probe)][wall_c(probe)]

		if (space == BOX):		# if space is a box
			probe += 1 			# start loop over
		elif (space == BAKGRD): # if space is
			push_move()
			loop = False
		elif (deteggt(space) == True): 	# if space is a egg
			if (wall_space == BLOCK) or (wall_space == KILLBLOCK):	# if next block after egg is a border
				kill_enemy(eggs, probe_r(probe), probe_c(probe))	# del egg from global egg list
				for i in range(len(push_eggs)): push_eggs[i] -= 1 	# subtract list refs in push_eggs
				play_audio('hatch')
				push_move()
				loop = False						# make space same as preceeding space
			else:
				for i in range(1, len(eggs)): # The first row of eggs[] is other information
					if ((eggs[i]['ro'] == probe_r(probe)) and (eggs[i]['co'] == probe_c(probe))):
						eggs.append(eggs.pop(i))
						push_eggs.append(0)
						break
				for i in range(len(push_eggs)):
					x = len(push_eggs) - i - 1
					push_eggs[i] = len(eggs) - x - 1
				probe += 1
		elif (space == BLOCK):				# if space is a border
			loop = False
		elif (space == KILLBLOCK):	 		# if space is a killblock
			play_audio('flatten')
			push_move()
			board[probe_r(probe - 1)][probe_c(probe - 1)] = KILLBLOCK
			lvl_box_cnt -= 1
			loop = False
		elif (space == BEAST): # if space is a beast
			if ((wall_space == KILLBLOCK) or (wall_space == BOX) or (wall_space == BLOCK)):
				kill_enemy(beasts, probe_r(probe), probe_c(probe))
				play_audio('squish')
				push_move()
			loop = False
		elif (space == MONSTER):# if space is a monster
			if ((wall_space == KILLBLOCK) or (wall_space == BLOCK)):
				kill_enemy(monsters, probe_r(probe), probe_c(probe))
				play_audio('squish')
				push_move()
			loop = False
		else:
			loop = False

def move_player(direction):
	global PLAYER, player, board, MOVES, BAKGRD, BOX, pulling

	row = player[1]['ro']
	col = player[1]['co']
	fow = row + MOVES[direction]['ra']
	fol = col + MOVES[direction]['ca']
	rtug = row - MOVES[direction]['ra']
	ctug = col - MOVES[direction]['ca']
	board[fow][fol] = PLAYER
	if (player[1]['tug']) and (board[rtug][ctug] == BOX):
		board[rtug][ctug] = BAKGRD
		board[row][col] = BOX
		player[1]['tug'] == False
	else:
		board[row][col] = BAKGRD
	player[1]['ro'] = fow
	player[1]['co'] = fol

def direct_move(tap_move):
	global player, MOVES, board, lowest_boxes, lvl_box_cnt

	space = board[player[1]['ro'] + MOVES[tap_move]['ra'] ][ player[1]['co'] + MOVES[tap_move]['ca'] ]

	if (space == BAKGRD):
		move_player(tap_move)
	elif (space == BOX):
		push_loop(tap_move)
	elif (space == MONSTER) or (space == BEAST) or (space == KILLBLOCK):
		if(plr_flash >= PLR_FLASHES): # player immunity while flashing
			kill_player()
			if space == KILLBLOCK:
				box_step = 0
				while(lvl_box_cnt < lowest_boxes):
					boxrow = randint(1, (board_rows - 1))
					boxcol = randint(1, (board_cols - 1))
					if(board[boxrow][boxcol] == BAKGRD):
						board[boxrow][boxcol] = BOX
						lvl_box_cnt += 1

def direct_keypress(tap):
	global player, MOVES, board, KEY_P_UP, KEY_P_DOWN, KEY_P_RIGHT, KEY_P_LEFT, KEY_UP, KEY_DOWN, KEY_RIGHT, KEY_LEFT, pulling

	if (tap == KEY_UP):
		direct_move('U')
	elif (tap == KEY_LEFT):
		direct_move('L')
	elif (tap == KEY_DOWN):
		direct_move('D')
	elif (tap == KEY_RIGHT):
		direct_move('R')
	if (tap == KEY_P_UP):
		player[1]['tug'] = True
		direct_move('U')
		player[1]['tug'] = False
	elif (tap == KEY_P_LEFT):
		player[1]['tug'] = True
		direct_move('L')
		player[1]['tug'] = False
	elif (tap == KEY_P_RIGHT):
		player[1]['tug'] = True
		direct_move('R')
		player[1]['tug'] = False
	elif (tap == KEY_P_DOWN):
		player[1]['tug'] = True
		direct_move('D')
		player[1]['tug'] = False


def pause():
	global board_rows, board_cols, left_margin, top_margin, keypress, term_cols, term_rows, game_play_mode

	game_play_mode = False

	def print_pause():
		print('\033[u\033[1B' + xbgx + chr(9556) + chr(9552)*12 + chr(9559))
		print('\033[u\033[2B' + xbgx + chr(9553) + '\033[12C' + chr(9553))
		print('\033[u\033[3B' + xbgx + chr(9553) + '\033[3CPAUSED\033[3C' + chr(9553))
		print('\033[u\033[4B' + xbgx + chr(9553) + '\033[12C' + chr(9553))
		print('\033[u\033[5B' + xbgx + chr(9562) + chr(9552)*12 + chr(9565))

	play_audio('pause')
	tbg(0) # handles transparent background
	set_midcent(6, 8)
	print_pause()
	keypress = 999

	while(True):
		if (keypress == ord('p')): break
		elif (keypress == 27):
			close_game()
		sleep(LCD_TIME)

	keypress = 999
	play_audio('pause')
	game_play_mode = True


def resize_terminal():
	global term_rows, term_cols, game_play_mode, keypress, xbgx, board

	keypress = 999
	while(keypress != ord('r')):
		system('clear')
		term_rows, term_cols = get_rw_cl_tcl(1,0,1)
		set_board_spacing()
		print_board(board)
		sleep(LCD_TIME)
		if game_play_mode:
			break

################################################################################################
############################################################-- Level Function --################
################################################################################################

def build_level():
	global GAME_LEVELS, NO_LIVES, NO_LEVEL, incubate, egg_speed, beast_speed, monster_speed, keypress
	global play_rows, play_cols, board_rows, board_cols, blank_board, board, term_cols, term_rows
	global newlevel, level, lives, score, mi1_opt, xbgx, fitted, trnsprnt
	global lvl_block_cnt, lvl_beast_cnt, lvl_monster_cnt, lvl_egg_cnt, lvl_box_cnt, block_type
	global BEAST, BAKGRD, BLOCK, KILLBLOCK, game_play_mode, top_margin, left_margin, LCD_TIME
	global KEY_UP, KEY_DOWN, KEY_RIGHT, KEY_LEFT, KEY_P_UP, KEY_P_DOWN, KEY_P_LEFT, KEY_P_RIGHT, pulling

	def print_beast():
		set_midcent(5,29)
		print('\033[u\033[0m' + BEAST*4 + BAKGRD*2 + BEAST*5 + BAKGRD*3 + BEAST*1 + BAKGRD*4 + BEAST*3 + BAKGRD*2 + BEAST*5)
		print('\033[u\033[1B\033[0m' + BEAST*1 + BAKGRD*3 + BEAST*1 + BAKGRD*1 + BEAST*1 + BAKGRD*6 + BEAST*1 + BAKGRD*1 + BEAST*1 + BAKGRD*2 + BEAST*1 + BAKGRD*3 + BEAST*1 + BAKGRD*3 + BEAST*1)
		print('\033[u\033[2B\033[0m' + BEAST*1 + BAKGRD*3 + BEAST*1 + BAKGRD*1 + BEAST*1 + BAKGRD*5 + BEAST*1 + BAKGRD*3 + BEAST*1 + BAKGRD*1 + BEAST*1 + BAKGRD*7 + BEAST*1)
		print('\033[u\033[3B\033[0m' + BEAST*4 + BAKGRD*2 + BEAST*3 + BAKGRD*3 + BEAST*5 + BAKGRD*2 + BEAST*3 + BAKGRD*4 + BEAST*1)
		print('\033[u\033[4B\033[0m' + BEAST*1 + BAKGRD*3 + BEAST*1 + BAKGRD*1 + BEAST*1 + BAKGRD*5 + BEAST*1 + BAKGRD*3 + BEAST*1 + BAKGRD*5 + BEAST*1 + BAKGRD*3 + BEAST*1)
		print('\033[u\033[5B\033[0m' + BEAST*1 + BAKGRD*3 + BEAST*1 + BAKGRD*1 + BEAST*1 + BAKGRD*5 + BEAST*1 + BAKGRD*3 + BEAST*1 + BAKGRD*1 + BEAST*1 + BAKGRD*3 + BEAST*1 + BAKGRD*3 + BEAST*1)
		print('\033[u\033[6B\033[0m' + BEAST*4 + BAKGRD*2 + BEAST*5 + BAKGRD*1 + BEAST*1 + BAKGRD*3 + BEAST*1 + BAKGRD*2 + BEAST*3 + BAKGRD*4 + BEAST*1)

	def print_note():
		set_botleft(1,0)
		print('\033[u\033[37m' + xbgx + 'Press \033[36mspacebar\033[37m to play \033[1;35mlevel ' + str(newlevel) + '\033[0m')
		set_botleft(0,0)
		print('\033[u\033[37m' + xbgx + 'Press \033[36mtab\033[37m for \033[1;35msettings\033[37m\033[0m')

	newlevel = 1
	lostlevels = 0
	wordvar = ''
	keypress = 999
########################################################-- Intro Screen (level 0)
	if (level == 0):
		sleep(1) # delay for effect
		print_board(blank_board)
		print_beast()
		play_audio('begin')
		sleep(.5) # delay to show options
#################################################################-- Clear Last Level
	if (lives == 0): ############### If the player lost the last level
		newlevel = level+1 - NO_LEVEL ### Death Level Penalty
		if newlevel < 1:
			newlevel = 1
			lostlevels = level+1 - newlevel
		if level > NO_LEVEL:
			lostlevels = NO_LEVEL
		if level == 1: wordvar = ' level'
		else: wordvar = ' levels'
		set_topleft(3,3)
		print('\033[u\033[37m' + xbgx + 'Player defeated. . .\033[u\033[2B' + xbgx + 'You lost \033[36m' + str(NO_LIVES) + ' points\033[37m and got held back \033[36m' + str(lostlevels) + wordvar + '.\033[37m\033[0m')
	else:
		newlevel = level + 1

	tbg(0)
	print_note()
################################################################-- Keyboard, Resize, Print, Loop
	keypress = 999
	while (True):
		if (keypress == ord(' ')):
			keypress = 999
			sleep(.8) # delay for effect before entering settings
			break
		if (keypress == 9):
			sleep(.4) # delay for effect before entering first level
			break
		if (level == 0 or keypress == ord('r')):
			tot_rows, tot_cols = get_rw_cl_tcl(1,0,1)
			if (tot_rows != term_rows) or (tot_cols != term_cols):
				if (level == 0):
					set_board_spacing()
					system('clear')
					tbg(0)
					print_board(blank_board)
					tbg(0)
					print_beast()
				if (level > 0):
					print_board(board)
				print_note()
				term_rows = tot_rows
				term_cols = tot_cols
		sleep(LCD_TIME)
#################################################################-- Prep New Level

	if (lives == 0): ############### If the player lost the last level
		lives = 5
		for i in range(1, len(player)): del player[1]
		for i in range(1, len(beasts)): del beasts[1]
		for i in range(1, len(monsters)): del monsters[1]
		for i in range(1, len(eggs)): del eggs[1]
	else: ########################## If the player won the last level
		for i in range(1, len(player)): del player[1]
	level = newlevel
	board = build_the_board()	# clears the board after end of level
	print_board(board)			# prints cleared board after end of level
	if (level <= (len(GAME_LEVELS) - 1)):
		lvl_beast_cnt = GAME_LEVELS[level-1]['beasts']
		lvl_monster_cnt = GAME_LEVELS[level-1]['monsters']
		lvl_egg_cnt = GAME_LEVELS[level-1]['eggs']
		if (GAME_LEVELS[level - 1]['block'] == 'yellow'): block_type = BLOCK
		if (GAME_LEVELS[level - 1]['block'] == 'orange'): block_type = KILLBLOCK
		if (GAME_LEVELS[level - 1]['blocks'] <= -1):
			lvl_block_cnt = int(play_rows * play_cols * .012)
		elif (abs(GAME_LEVELS[level - 1]['blocks']) < 1):
			lvl_block_cnt = play_rows * play_cols * .012
			lvl_block_cnt = int(lvl_block_cnt + (lvl_block_cnt * GAME_LEVELS[level - 1]['blocks']))
		else:
			lvl_block_cnt = GAME_LEVELS[level - 1]['blocks']
		if (GAME_LEVELS[level - 1]['boxes'] <= -1):
			lower_boxes = int(play_rows * play_cols / 4 - 10)
			upper_boxes = int(play_rows * play_cols / 4 + 10)
			lvl_box_cnt = randint(lower_boxes, upper_boxes) # Default Level Boxes
		elif (abs(GAME_LEVELS[level - 1]['boxes'] < 1)):
			lower_boxes = int(play_rows * play_cols / 4 - 10)
			upper_boxes = int(play_rows * play_cols / 4 + 10)
			lvl_box_cnt = randint(lower_boxes, upper_boxes) # Default Level Boxes
			lvl_box_cnt = int(lvl_box_cnt + (lvl_box_cnt * GAME_LEVELS[level - 1]['boxes']))
		else:
			lvl_box_cnt = GAME_LEVELS[level - 1]['boxes']
	else:
		lvl_beast_cnt =	int(level / 3)
		lvl_monster_cnt = int(level / 3)
		lvl_egg_cnt = int(level / 3)
		if (level % 2 == 0): block_type = KILLBLOCK
		else: block_type = BLOCK
		if (level % 3) == 1: lvl_beast_cnt += 1
		elif (level % 3) == 2:
			lvl_beast_cnt += 1
			lvl_egg_cnt += 1
		lvl_block_cnt = int(play_rows * play_cols * .012)
		lower_boxes = int(play_rows * play_cols / 4 - 10)
		upper_boxes = lower_boxes + 20
		lvl_box_cnt = randint(lower_boxes, upper_boxes) # Default Level Boxes
	if lvl_box_cnt < lowest_boxes: lvl_box_cnt = lowest_boxes # Lowest number of boxes set at beginning of script
#################################################################-- Settings Variables
	main_menu_tab = 0
	item_menu = 0
	controls_menu = 9
	#tbg(0) # handles transparent background
	if trnsprnt: xbgx = '\033[49m'
	dim = '\033[0m' + xbgx + '\033[2m'
	norm = '\033[0m' + xbgx
	ltab = '\033[0m\033[7m' + xbgx
	dtab = '\033[0m\033[7m' + xbgx + '\033[2m'
	speedbg = xbgx + '\033[34m|||\033[32m|||||\033[33m\033[31m||\033[37m' + xbgx
	speed_arrow = xbgx + '\033[1;35m' + chr(9632) + xbgx	 # 10219 (thin double) 9193 (skip) 9670 (diamon)
	chr_cnt = 0
	mi1_shade = '' ########### 1 -- direction keys group
	#mi1_opt = #  (set globally at the beginning of the script)
	mi2_shade = '' ########### 2 -- block-pull method
	mi2_opt = 1
	mi3_shade = '' ############ 3 -- level beast count
	mi4_shade = '' ############ 4 -- level monster count
	mi5_shade = '' ############ 5 -- level egg count
	mi6_shade = '' ############ 6 -- level box count
	mi7_shade = '' ############ 7 -- level block count
	mi8_shade = '' ############ 8 -- level block type
	mi8_opt = 0
	if block_type == BLOCK: mi8_opt = 1
	elif block_type == KILLBLOCK: mi8_opt = 2
	normalyellow, dangerousorange = '', ''
	mi9_shade = '' ############ 9 -- beast speed
	beast_speed_min = .3
	beast_speed_max = 2.3
	beast_speed_inc = .2
	beast_speed = beast_speed - (beast_speed % beast_speed_inc)
	if (beast_speed > beast_speed_max): beast_speed = beast_speed_max
	elif (beast_speed < beast_speed_min): beast_speed = beast_speed_min
	beast_arrows = int((beast_speed - beast_speed_min ) / beast_speed_inc)
	mi10_shade = '' ########## 10 -- monster speed
	monster_speed_min = .3
	monster_speed_max = 2.3
	monster_speed_inc = .2
	monster_speed = monster_speed - (monster_speed % monster_speed_inc)
	if (monster_speed > monster_speed_max): monster_speed = monster_speed_max
	elif (monster_speed < monster_speed_min): monster_speed = monster_speed_min
	monster_arrows = int((monster_speed - monster_speed_min) / monster_speed_inc)
	mi11_shade = '' ########## 11 -- egg incubation time
	incubate_min = 4
	incubate_max = 40
	incubate_inc = 4
	incubate = incubate - (incubate % incubate_inc)
	if (incubate > incubate_max): incubate = incubate_max
	elif (incubate < incubate_min): incubate = incubate_min
	incubate_arrows = int((incubate - incubate_min) / incubate_inc)
	mi12_shade = '' ########## 12 -- egg countdown speed
	timer_min = .5
	timer_max = 5
	timer_inc = .5
	egg_speed = egg_speed - (egg_speed % timer_inc)
	if (egg_speed > timer_max): egg_speed = timer_max
	elif (egg_speed < timer_min): egg_speed = timer_min
	timer_arrows = int((egg_speed - timer_min) / timer_inc)
#################################################################-- Settings Functions
	def dim_menus(mi):
		global mi1_shade, mi2_shade, mi3_shade, mi4_shade, mi5_shade, mi6_shade, mi7_shade, mi8_shade, mi9_shade, mi10_shade, mi11_shade, mi12_shade

		if mi != 1: mi1_shade = dim ########### 1 -- direction keys group
		else: mi1_shade = norm
		if mi != 2: mi2_shade = dim ########### 2 -- block-pull method
		else: mi2_shade = norm
		if mi != 3: mi3_shade = dim ########### 3 -- level beast count
		else: mi3_shade = norm
		if mi != 4: mi4_shade = dim ########### 4 -- level monster count
		else: mi4_shade = norm
		if mi != 5: mi5_shade = dim ########### 5 -- level egg count
		else: mi5_shade = norm
		if mi != 6: mi6_shade = dim ########### 6 -- level box count
		else: mi6_shade = norm
		if mi != 7: mi7_shade = dim ########### 7 -- level block count
		else: mi7_shade = norm
		if mi != 8: mi8_shade = dim ########### 8 -- level block type
		else: mi8_shade = norm
		if mi != 9: mi9_shade = dim ########### 9 -- beast speed
		else: mi9_shade = norm
		if mi != 10: mi10_shade = dim ######## 10 -- monster speed
		else: mi10_shade = norm
		if mi != 11: mi11_shade = dim ######## 11 -- egg incubation time
		else: mi11_shade = norm
		if mi != 12: mi12_shade = dim ######## 12 -- egg countdown speed
		else: mi12_shade = norm
	def main_menu_1(): #### -- First Tab
		global mi1_opt, mi1_shade, mi2_shade, wasd, arrows, vi, pulling, single, toggle, auto

		print('\033[u\033[2B' + mi1_shade + 'Movement Keys: ' + wasd + mi1_shade + arrows + mi1_shade + vi)

		print('\033[u\033[6B\033[0m' + xbgx + '\033[37m' + ' '*4 + 'Hold the \033[36mShift \033[37mkey down to pull boxes.\033[0m')

	def main_menu_2():
		global mi3_shade, mi4_shade, mi5_shade, mi6_shade, mi7_shade, mi8_shade, BLOCK, block_type, KILLBLOCK, normalyellow, dangerousorange,  play_rows, play_cols
		global lvl_beast_cnt, lvl_monster_cnt, lvl_egg_cnt

		print('\033[u\033[3B\033[34C' + xbgx + 'Total Spaces: \033[36m' + str(play_rows * play_cols) + ' \033[37m')
		print('\033[u\033[4B\033[35C' + xbgx + 'Used Spaces: \033[36m' + str(lvl_box_cnt + lvl_block_cnt + lvl_monster_cnt + lvl_beast_cnt + lvl_egg_cnt) + ' \033[37m')
		print('\033[u\033[5B\033[35C' + xbgx + 'Free Spaces: \033[36m' + str((play_rows * play_cols) - (lvl_block_cnt + lvl_box_cnt + lvl_monster_cnt + lvl_beast_cnt + lvl_egg_cnt)) + ' \033[37m')

		print('\033[u\033[2B' 	+ mi3_shade 	+ BEAST 			+ mi3_shade + xbgx + ' - Beast Count: \033[1;35m' + str(lvl_beast_cnt) + ' \033[37m')
		print('\033[u\033[4B' 	+ mi4_shade 	+ MONSTER 			+ mi4_shade + xbgx + ' - Monster Count: \033[1;35m' + str(lvl_monster_cnt) + ' \033[37m')
		print('\033[u\033[6B' 	+ mi5_shade 	+ chr(11052) + ' ' 	+ mi5_shade + xbgx + ' - Egg Count: \033[1;35m' + str(lvl_egg_cnt) + ' \033[37m')
		print('\033[u\033[8B' 	+ mi6_shade 	+ BOX 				+ mi6_shade + xbgx + ' - Box Count: \033[1;35m' + str(lvl_box_cnt) + ' \033[37m')
		print('\033[u\033[10B' 	+ mi7_shade 	+ block_type 		+ mi7_shade + xbgx + ' - Block Count: \033[1;35m' + str(lvl_block_cnt) + ' \033[37m')
		print('\033[u\033[12B' 	+ mi8_shade 	+ block_type 		+ mi8_shade + xbgx + ' - Block Type: ' + normalyellow + mi8_shade + dangerousorange + mi8_shade + ' \033[37m')

	def main_menu_3():
		global mi9_shade, mi10_shade, mi11_shade, mi12_shade, incubate
		print('\033[u\033[2B' + mi9_shade 	+ BEAST 					+ mi9_shade 	+ ' - Beast:           slower ' + speedbg + ' faster\033[' + str(beast_arrows + 8) +    'D' + speed_arrow + '\033[30m')
		print('\033[u\033[4B' + mi10_shade 	+ MONSTER 					+ mi10_shade	+ ' - Monster:         slower ' + speedbg + ' faster\033[' + str(monster_arrows + 8) +  'D' + speed_arrow + '\033[30m')
		print('\033[u\033[6B' + mi11_shade 	+ chr(11052) + ' ' 			+ mi11_shade 	+ ' - Egg Incubate:    slower ' + speedbg + ' faster\033[' + str(incubate_arrows + 8) + 'D' + speed_arrow + '\033[30m')
		print('\033[u\033[8B' + mi12_shade 	+ chr(11052) + chr(8320) 	+ mi12_shade 	+ ' - Egg Timer:       slower ' + speedbg + ' faster\033[' + str(timer_arrows + 8) +    'D' + speed_arrow + '\033[30m')

	def mi1_controls(opt):
		global dir_keys, wasd, arrows, vi, pulling, KYBD, KEY_UP, KEY_DOWN, KEY_RIGHT, KEY_LEFT, KEY_P_UP, KEY_P_DOWN, KEY_P_RIGHT, KEY_P_LEFT
		if opt == 1:
			dir_keys = 0
			wasd = '\033[1:37m[\033[1;35m ' + KYBD[0]['title'] + ' \033[1;37m]\033[0m'
			arrows = '  ' + KYBD[1]['title'] + '  '
			vi = '  ' + KYBD[2]['title'] + '  '

		elif opt == 2:
			dir_keys = 1
			wasd = '  ' + KYBD[0]['title'] + '  '
			arrows = '\033[1;37m[\033[1;35m ' + KYBD[1]['title'] + ' \033[1;37m]\033[0m'
			vi = '  ' + KYBD[2]['title'] + '  '

		elif opt == 3:
			dir_keys = 2
			wasd = '  ' + KYBD[0]['title'] + '  '
			arrows = '  ' + KYBD[1]['title'] + '  '
			vi = '\033[1;37m[\033[1;35m ' + KYBD[2]['title'] + ' \033[1;37m]\033[0m'

		KEY_UP = KYBD[dir_keys]["K_UP"]
		KEY_DOWN = KYBD[dir_keys]["K_DOWN"]
		KEY_RIGHT = KYBD[dir_keys]["K_RIGHT"]
		KEY_LEFT = KYBD[dir_keys]["K_LEFT"]
		KEY_P_UP = KYBD[dir_keys]["PK_UP"]
		KEY_P_DOWN = KYBD[dir_keys]["PK_DOWN"]
		KEY_P_RIGHT = KYBD[dir_keys]["PK_RIGHT"]
		KEY_P_LEFT = KYBD[dir_keys]["PK_LEFT"]

	def mi2_controls(opt):
		global pulling, toggle, single, auto, hold

		if opt == 1:
			pulling = 'hold'
			hold = '\033[1;37m[\033[1;35m hold \033[1;37m]\033[0m'
			toggle = '  toggle  '
			single = '  single  '
			auto = '  auto  '


	def mi8_controls(opt):
		global block_type, BLOCK, KILLBLOCK, normalyellow, dangerousorange

		if opt == 1:
			block_type = BLOCK
			normalyellow = '\033[1;37m[\033[1;35m Normal Yellow \033[1;37m]\033[0m'
			dangerousorange = '  Dangerous Orange  '
		elif opt == 2:
			block_type = KILLBLOCK
			normalyellow = '  Normal Yellow  '
			dangerousorange = '\033[1;37m[\033[1;35m Dangerous Orange \033[1;37m]\033[0m'

	def tabkey_note():
		global xbgx

		set_botleft(1,0)
		print('\033[u\033[0m' + xbgx + '\033[37mPress \033[36mspacebar\033[37m to play \033[1;35mlevel ' + str(newlevel) + '\033[0m')
		set_botleft(0,0)
		print('\033[u\033[0m' + xbgx + '\033[37mPress \033[36mtab \033[37mto switch settings tabs\033[0m')


	dim_menus(0)
	mi1_controls(mi1_opt)
	mi2_controls(mi2_opt)
	mi8_controls(mi8_opt)
	tab_line = 20
	if play_cols < 40: tab_line = 24 + play_cols - 40 # Based on smallest playboard size = 16 x 30 (18 x 32 with borders)
	else: tab_line = 20
	if keypress == 9:
		print_board(blank_board) ######################################################-- print_board
		show_tabkey_note = True
		################################################################################################
		while (True):######################################-- Settings Menu Frame-Draw Loop --##########
		################################################################################################

			if keypress == ord(' '): # spacebar exits the settings menu
				keypress = 999
				sleep(.3) # delay for effect, before exiting the settings menu
				print_board(blank_board) ######################################################-- print_board
				sleep(.5) # delay for effect, after exiting the settings menu
				break
			elif keypress == 9: ####-- spacebar key switches tabs
				keypress = 999
				main_menu_tab += 1
				play_audio('menu_tab')
				if main_menu_tab > 3:
					main_menu_tab = 1
				if main_menu_tab == 1:
					print_board(blank_board) ######################################################-- print_board
					if keypress != 9 and show_tabkey_note == True: tabkey_note()
					show_tabkey_note = False
					item_menu = 0
					dim_menus(0)
					set_topleft(0,0)
					print('\033[u' + norm + chr(9473)
						+ dtab + ' key options ' + norm + chr(9473)
						+ dtab + ' level setup ' + norm + chr(9473)
						+ dtab + ' pawn speeds ' + norm + chr(9473)*tab_line)
					sleep(.07) # delay between tab switches for audio sync
					print('\033[u' + norm + chr(9473)
						+ ltab + ' key options ' + norm + chr(9473)
						+ dtab + ' level setup ' + norm + chr(9473)
						+ dtab + ' pawn speeds ' + norm + chr(9473)*tab_line)
				elif main_menu_tab == 2:
					print_board(blank_board) ######################################################-- print_board
					item_menu = 2
					dim_menus(2)
					set_topleft(0,0)
					print('\033[u' + norm + chr(9473)
						+ dtab + ' key options ' + norm + chr(9473)
						+ dtab + ' level setup ' + norm + chr(9473)
						+ dtab + ' pawn speeds ' + norm + chr(9473)*tab_line)
					sleep(.07) # delay between tab switches for audio sync
					print('\033[u' + norm + chr(9473)
						+ dtab + ' key options ' + norm + chr(9473)
						+ ltab + ' level setup ' + norm + chr(9473)
						+ dtab + ' pawn speeds ' + norm + chr(9473)*tab_line)
				elif main_menu_tab == 3:
					print_board(blank_board) ######################################################-- print_board
					item_menu = 8
					dim_menus(8)
					set_topleft(0,0)
					print('\033[u' + norm + chr(9473)
						+ dtab + ' key options ' + norm + chr(9473)
						+ dtab + ' level setup ' + norm + chr(9473)
						+ dtab + ' pawn speeds ' + norm + chr(9473)*tab_line)
					sleep(.07) # delay between tab switches for audio sync
					print('\033[u' + norm + chr(9473)
						+ dtab + ' key options ' + norm + chr(9473)
						+ dtab + ' level setup ' + norm + chr(9473)
						+ ltab + ' pawn speeds ' + norm + chr(9473)*tab_line)
			if main_menu_tab == 1:
				main_menu_1()
			elif main_menu_tab == 2:
				main_menu_2()
			elif main_menu_tab == 3:
				main_menu_3()

			if ((keypress == KEY_UP) or (keypress == KEY_DOWN)):
				if (main_menu_tab == 1):

					main_menu_1()
					if (keypress == KEY_UP):
						item_menu -= 1
						if item_menu < 1: item_menu = 2
						keypress = 999
					elif (keypress == KEY_DOWN):
						item_menu += 1
						if item_menu > 2: item_menu = 1
						keypress = 999
					if (item_menu != 0):
						play_audio('menu_item')
					if (item_menu == 1): dim_menus(1)
					elif (item_menu == 2): dim_menus(2)
				elif (main_menu_tab == 2):
					main_menu_2()
					if (keypress == KEY_UP):
						item_menu -= 1
						if item_menu < 3:
							item_menu = 8
						keypress = 999
					elif (keypress == KEY_DOWN):
						item_menu += 1
						if item_menu > 8:
							item_menu = 3
						keypress = 999
					if (item_menu != 2):
						play_audio('menu_item')
					if (item_menu == 3): dim_menus(3)
					elif (item_menu == 4): dim_menus(4)
					elif (item_menu == 5): dim_menus(5)
					elif (item_menu == 6): dim_menus(6)
					elif (item_menu == 7): dim_menus(7)
					elif (item_menu == 8): dim_menus(8)
				elif (main_menu_tab == 3):
					main_menu_3()
					if (keypress == KEY_UP):
						item_menu -= 1
						if item_menu < 9:
							item_menu = 12
						keypress = 999
					elif (keypress == KEY_DOWN):
						item_menu += 1
						if item_menu > 12:
							item_menu = 9
						keypress = 999
					if (item_menu != 8):
						play_audio('menu_item')
					if (item_menu == 9): dim_menus(9)
					elif (item_menu == 10): dim_menus(10)
					elif (item_menu == 11): dim_menus(11)
					elif (item_menu == 12): dim_menus(12)
			elif ((keypress == KEY_LEFT) or (keypress == KEY_RIGHT)):
				maxed_cnt = (play_rows * play_cols) - (lvl_block_cnt + lvl_box_cnt + lvl_monster_cnt + lvl_beast_cnt + lvl_egg_cnt)
				if (main_menu_tab == 1) and (item_menu == 1):
					if (keypress == KEY_LEFT):
						mi1_opt -= 1
						if mi1_opt < 1: mi1_opt = 3
					elif (keypress == KEY_RIGHT):
						mi1_opt += 1
						if mi1_opt > 3: mi1_opt = 1
					if mi1_opt == 1:
						mi1_controls(1)
					elif mi1_opt == 2:
						mi1_controls(2)
					elif mi1_opt == 3:
						mi1_controls(3)
					play_audio('menu_item_tick')
					keypress = 999
				#elif (main_menu_tab == 1) and (item_menu == 2):
					#if (keypress == KEY_LEFT):
					#	mi2_opt -= 1
					#	if mi2_opt < 1: mi2_opt = 4
					#elif (keypress == KEY_RIGHT):
					#	mi2_opt += 1
					#	if mi2_opt > 4: mi2_opt = 1
					#if mi2_opt == 1: mi2_controls(1)
					#elif mi2_opt == 2: mi2_controls(2)
					#elif mi2_opt == 3: mi2_controls(3)
					#elif mi2_opt == 4: mi2_controls(4)
					#if item_menu != 3: play_audio('menu_item_tick')
					#keypress = 999

				elif (main_menu_tab == 2) and (item_menu == 3):
					if (keypress == KEY_LEFT):
						lvl_beast_cnt -= 1
						if lvl_beast_cnt < 0:
							lvl_beast_cnt = 0
							play_audio('flatten')
						else:
							play_audio('menu_item_tick')
					elif (keypress == KEY_RIGHT):
						lvl_beast_cnt += 1
						if lvl_beast_cnt > maxed_cnt:
							lvl_beast_cnt = maxed_cnt
							play_audio('flatten')
						else:
							play_audio('menu_item_tick')
					keypress = 999
				elif (main_menu_tab == 2) and (item_menu == 4):
					if (keypress == KEY_LEFT):
						lvl_monster_cnt -= 1
						if lvl_monster_cnt < 0:
							lvl_monster_cnt = 0
							play_audio('flatten')
						else:
							play_audio('menu_item_tick')
					elif (keypress == KEY_RIGHT):
						lvl_monster_cnt += 1
						if lvl_monster_cnt > maxed_cnt:
							lvl_monster_cnt = maxed_cnt
							play_audio('flatten')
						else:
							play_audio('menu_item_tick')
					keypress = 999
				elif (main_menu_tab == 2) and (item_menu == 5):
					if (keypress == KEY_LEFT):
						lvl_egg_cnt -= 1
						if lvl_egg_cnt < 0:
							lvl_egg_cnt = 0
							play_audio('flatten')
						else:
							play_audio('menu_item_tick')
					elif (keypress == KEY_RIGHT):
						lvl_egg_cnt += 1
						if lvl_egg_cnt > maxed_cnt:
							lvl_egg_cnt = maxed_cnt
							play_audio('flatten')
						else:
							play_audio('menu_item_tick')
					keypress = 999
				elif (main_menu_tab == 2) and (item_menu == 6):
					if (keypress == KEY_LEFT):
						lvl_box_cnt -= 1
						if lvl_box_cnt < 0:
							lvl_box_cnt = 0
							play_audio('flatten')
						else:
							play_audio('menu_item_tick')
					elif (keypress == KEY_RIGHT):
						lvl_box_cnt += 1
						if lvl_box_cnt > maxed_cnt:
							lvl_box_cnt = maxed_cnt
							play_audio('flatten')
						else:
							play_audio('menu_item_tick')
					keypress = 999
				elif (main_menu_tab == 2) and (item_menu == 7):
					if (keypress == KEY_LEFT):
						lvl_block_cnt -= 1
						if lvl_block_cnt < 0:
							lvl_block_cnt = 0
							play_audio('flatten')
						else:
							play_audio('menu_item_tick')
					elif (keypress == KEY_RIGHT):
						lvl_block_cnt += 1
						if lvl_block_cnt > maxed_cnt:
							lvl_block_cnt = maxed_cnt
							play_audio('flatten')
						else:
							play_audio('menu_item_tick')
					keypress = 999
				elif (main_menu_tab == 2) and (item_menu == 8):
					if (keypress == KEY_LEFT):
						mi8_opt -= 1
						if mi8_opt < 1: mi8_opt = 2
					elif (keypress == KEY_RIGHT):
						mi8_opt += 1
						if mi8_opt > 2: mi8_opt = 1
					if mi8_opt == 1: mi8_controls(1)
					elif mi8_opt == 2: mi8_controls(2)
					play_audio('menu_item_tick')
					keypress = 999
				elif (main_menu_tab == 3) and (item_menu == 9):
					if (keypress == KEY_RIGHT):
						beast_speed -= beast_speed_inc
						if beast_speed < beast_speed_min:
							beast_speed = beast_speed_min
							play_audio('flatten')
						else:
							play_audio('menu_item_tick')
					elif (keypress == KEY_LEFT):
						beast_speed += beast_speed_inc
						if beast_speed > beast_speed_max:
							beast_speed = beast_speed_max
							play_audio('flatten')
						else:
							play_audio('menu_item_tick')
					beast_arrows = int((beast_speed - beast_speed_min ) / beast_speed_inc)
					keypress = 999
				elif (main_menu_tab == 3) and (item_menu == 10):
					if (keypress == KEY_RIGHT):
						monster_speed -= monster_speed_inc
						if monster_speed < monster_speed_min:
							monster_speed = monster_speed_min
							play_audio('flatten')
						else:
							play_audio('menu_item_tick')
					elif (keypress == KEY_LEFT):
						monster_speed += monster_speed_inc
						if monster_speed > monster_speed_max:
							monster_speed = monster_speed_max
							play_audio('flatten')
						else:
							play_audio('menu_item_tick')
					monster_arrows = int((monster_speed - monster_speed_min ) / monster_speed_inc)
					keypress = 999
				elif (main_menu_tab == 3) and (item_menu == 11):
					if (keypress == KEY_RIGHT):
						incubate -= incubate_inc
						if incubate < incubate_min:
							incubate = incubate_min
							play_audio('flatten')
						else:
							play_audio('menu_item_tick')
					elif (keypress == KEY_LEFT):
						incubate += incubate_inc
						if incubate > incubate_max:
							incubate = incubate_max
							play_audio('flatten')
						else:
							play_audio('menu_item_tick')
					incubate_arrows = int((incubate - incubate_min ) / incubate_inc)
					keypress = 999
				elif (main_menu_tab == 3) and (item_menu == 12):
					if (keypress == KEY_RIGHT):
						egg_speed -= timer_inc
						if egg_speed < timer_min:
							egg_speed = timer_min
							play_audio('flatten')
						else:
							play_audio('menu_item_tick')
					elif (keypress == KEY_LEFT):
						egg_speed += timer_inc
						if egg_speed > timer_max:
							egg_speed = timer_max
							play_audio('flatten')
						else:
							play_audio('menu_item_tick')
					timer_arrows = int((egg_speed - timer_min ) / timer_inc)
					keypress = 999

########################################################################################################
#######################################################################-- End of Settings Loop --#######
########################################################################################################

	box_step = 0
	block_step = 0
	blockrow = 0
	blockcol = 0
	boxrow = 0
	boxcol = 0
	while(block_step < lvl_block_cnt):
		blockrow = randint(1, (board_rows - 1))
		blockcol = randint(1, (board_cols - 1))
		if(board[blockrow][blockcol] == BAKGRD):
			board[blockrow][blockcol] = block_type
			block_step += 1

	while(box_step < lvl_box_cnt):
		boxrow = randint(1, (board_rows - 1))
		boxcol = randint(1, (board_cols - 1))
		if(board[boxrow][boxcol] == BAKGRD):
			board[boxrow][boxcol] = BOX
			box_step += 1

	place_beasts(lvl_beast_cnt)
	place_monsters(lvl_monster_cnt)
	place_eggs(lvl_egg_cnt)
	place_player()

	game_play_mode = False

	play_audio('begin')
################################################################################################
###########################################################-- Input Function --#################
################################################################################################

def take_input():
	global pulling, gameterm, debug, keypress, player, top_margin, left_margin, key_move, game_play_mode, term_cols, term_rows

	noecho()

	while(True):
		sleep(LCD_TIME - .009) # keeps the input loop sane. works faster than the game loop
		keypress = gameterm.getch()
		if (game_play_mode):
			if keypress == ord('r'):
				resize_terminal()
				keypress = 999
			elif keypress == ord('b'):
				if debug == True:
					debug = False
					set_board_spacing()
					system('clear')
				else:
					debug = True
					set_board_spacing()
					system('clear')
			direct_keypress(keypress)

################################################################################################
##################-- This is the beginning of the program's main execution --###################
################################################################################################

try:
	print('\033[?25')
	gameterm = initscr()
	noecho()
	gameterm.keypad(1)
	main_input = Thread(target=take_input)
	main_input.daemon = True
	main_input.start()
	set_board_spacing()
	board = build_the_board()
	blank_board = build_the_board()
	level = 0
	newlevel = 0
	score = 0
	build_level()
	game_play_mode = True
	exec_start = 0
	exec_end = 0
	exec_time = 0

	while(True):
		if(lives == 0) or ((len(beasts) == 1) and (len(monsters) == 1) and (len(eggs) == 1)):
			game_play_mode = False
			if lives == 0:
				play_audio('loss')
				score -= NO_LIVES # Death Point Penalty
			elif level != 0:
				play_audio('win')
				score += WIN_LEVEL # Reward for clearing level
			print_board(board)	# prints the board after the level is over
			sleep(1.3) 			# shows the board after the level is over
			build_level()		# builds next level
			game_play_mode = True
		else:
			if keypress == ord('p'):
				pause()
			exec_start = time()
			flash_player()
			move_enemies(beasts)
			move_enemies(monsters)
			hatch_eggs()
			print_board(board)
			exec_end = time()
			exec_time = exec_end - exec_start
		if (LCD_TIME > exec_time):
			sleep(LCD_TIME - exec_time) # main game loop (compensates for frame execution time)
		if keypress == 27: close_game()
except KeyboardInterrupt:
	close_game()
