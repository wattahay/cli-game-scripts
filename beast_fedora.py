#!/usr/bin/env python
from curses import initscr
from random import randint, choices
from os import system, popen
from time import sleep
from threading import Thread
##################################-- starting game statistics
lives = 5		# starting lives
###############################
beast_speed = 1.5	# seconds between enemy moves
monster_speed = 1.1	# seconds between enemy moves
egg_speed = 3		# seconds between countdown
incubate = 3
##################################-- game scoring balance
beast_scr = 2		# points for killing beasts
egg_scr = 4		# points for killing eggs
monster_scr = 6		# points for killing monsters
##################################-- game speed
LCD_TIME = .04
####################################-- move constants
MOVES = {
 'U': {	'ra':-1,	'ca':0	}, 	# ra - "row adjustment"
 'D': {	'ra':1, 	'ca':0	},	# ca - "column adjustment"
 'L': {	'ra':0, 	'ca':-1	},
 'R': {	'ra':0, 	'ca':1	},
'UL': {	'ra':-1, 	'ca':-1	},
'UR': {	'ra':-1, 	'ca':1	},
'DL': {	'ra':1, 	'ca':-1	},
'DR': {	'ra':1, 	'ca':1	}
}

KEY_UP = 259
KEY_DOWN = 258
KEY_RIGHT = 261
KEY_LEFT = 260
KEY_P_DOWN = 0
KEY_P_RIGHT = 0
KEY_P_LEFT = 0
KEY_P_UP = 0

mi1_opt = 2
keypress = '' 
debug = False
last_frame = 1
timeout = 0
pulling = 'hold' # 'hold / 'tog' /  'swi' / 'sin'
game_play_mode = False
##################################-- formatted character constants
# (ANSI styles)	 FG   + 	BG   + 		Style +		Characters +			Reset
BAKGRD 	  =			'\033[40m' +			'  ' 
BLOCK 	  =       		'\033[43m' +	       		'  ' + 				'\033[0m'
KILLBLOCK = 	'\033[31m'	'\033[43m' + '\033[7m\033[2m' + chr(9618) + chr(9618) + 	'\033[0m'
BOX 	  =	'\033[32m' +	'\033[40m' +			chr(9618) + chr(9618) +		'\033[0m'
XPBOX 	  = 	'\033[32m' + 	'\033[40m' +	'\033[2m' +	chr(9618) + chr(9618) + 	'\033[0m'
BEAST 	  = 	'\033[31m' +	'\033[40m' +			chr(9500) + chr(9508) +		'\033[0m'
MONSTER   = 	'\033[31m' +	'\033[40m' +			chr(9568) + chr(9571) +		'\033[0m'
PLAYER    = 	'\033[34m' +	'\033[40m' +			chr(9664) + chr(9654) +		'\033[0m'
# http://wiki.bash-hackers.org/scripting/terminalcodes
eggsub = 8329			# unicode key for subscript 9 (8328 = 8, and so on)
egg2nd = 32			# unicode key for a space character 
def EGG(sub):
	return '\033[37m\033[40m\033[2m' + chr(11052) + '\033[1m' + chr(sub) + '\033[0m'

def deteggt(chegg):
	if (chegg[0:15] == '\033[37m\033[40m\033[2m' + chr(11052)): return True
###################################-- Pawn Classes (Dictionaries)
beasts = [{
	'frames': (int(beast_speed / LCD_TIME)),
	'frame':0,
	'chr': BEAST,
	'pnts': beast_scr 
	}]

monsters = [{
	'frames': (int(monster_speed / LCD_TIME)),
	'frame':0,
	'chr': MONSTER,
	'pnts': monster_scr
	}]

eggs = [{
	'frames': (int(egg_speed / LCD_TIME)),
	'frame':0,
	'incu_frames': (int(1 / LCD_TIME)), # incu_frames add up to 1 second
	'incu_frame': 0,
	'pnts': egg_scr
	}]
# 'sub'		updated digital unicode reference to subscript character
# 'wait'	randomized wait time before hatching countdown
player = [{
		'flash_frames': (int(.05 / LCD_TIME) * 2),
		'chr': PLAYER,
		'pnts': 10 
	}]

plr_flashes = 5
plr_flash = 0
plr_frames = (int(.05 / LCD_TIME) * 2)
plr_frame = 0
	
# 'tug'
# 'ro'		row
# 'co'		col
# 'stg'		"stagger" (frame of movement) compared to others
################################################################################################
####################################################################-- level 1 setup --#########
################################################################################################
level = 0	# change in order to start on a specific level
score = 0	# in-game total score
points = 0	# in-game level points added at end of level
################################################################################################
board = [] #########################################################-- board setup --###########
blank_board = [] ###############################################################################
reset_board = [] ###########-- classic board size variables
play_rows = 20	# only change this in-game
play_cols = 40	# only change this in-game
board_rows = play_rows + 2
board_cols = play_cols + 2
######################################-- board dimensions
classic = True
left_margin = 0 
top_margin = 0
stat_rows = 3

def plan_the_board(): #{

	global save_top, save_left, top_margin, left_margin, board_rows, board_cols, play_rows, play_cols, stat_rows, stat_space, classic, ttyCols, ttyRows

	ttyRows, ttyCols = popen('stty size', 'r').read().split()
	ttyRows = int(ttyRows)
	ttyCols = int(ttyCols)
	screen_rows = ttyRows
	screen_cols = int(ttyCols / 2)

	if (screen_cols < 44) & (ttyRows < 28):	classic = False
	elif (ttyCols < 60) & (ttyRows < 20):
		print('This area is impossibly small')
		sleep(3)
		system('reset')
	else: classic = True

	if (classic):
		board_rows = play_rows + 2
		board_cols = play_cols + 2
		top_margin = int((screen_rows - board_rows - stat_rows) / 2)
		left_margin = int((ttyCols - board_cols*2) / 2)
	else:
		stat_space = 0
		board_rows = screen_rows - stat_rows - 1 
		board_cols = screen_cols
		top_margin = 0
		left_margin = 0

	save_top = top_margin # assigned for the debug feature 
	save_left = left_margin # assigned for the debug feature
	stat_space = int((board_cols * 2 - (4 * 14 )) / 5) # calculate this for the print_board function
	if stat_space < 0: stat_space = 0
	#}
# BUILDS a blank board
def build_the_board(): #{
	global board_cols, board_rows

	screen_board = []

	for rowi in range(board_rows): # builds the board based on 'board_rows' and 'board_cols' which includes room for borders
		screen_board.append([])
		for coli in range(board_cols):
			screen_board[rowi].append([])
			screen_board[rowi][coli] = BAKGRD

	for rowi in range(board_rows): # draws the game boarders on the board
		for coli in range(board_cols):
			if(rowi == 0) | (rowi == (board_rows - 1)) | (coli == 0) | (coli == (board_cols - 1)):
				screen_board[rowi][coli] = BLOCK

	return screen_board
#}
board = build_the_board()
reset_board = build_the_board()
blank_board = build_the_board()
########################################################-- set cursor functions
def set_topleft_ref(top, left):
	global top_margin, left_margin
	print('\033[?25l\033[' + str(top_margin + top)  + ';' + str(left_margin + left) + 'H\033[s\033[0m')

def set_topmid_ref(top, leftkeel):
	global top_margin, left_margin, board_cols	
	print('\033[' + str(top_margin + 1 + top) + ';' + str(left_margin + int(board_cols) - leftkeel) + 'H\033[s\033[0m')

def set_cursor_avoid():
	global top_margin, left_margin, board_rows
	print('\033[' + str(top_margin + board_rows) + ';0H\033[0m\033[30m')
######################################################-- print board function
def print_board(board_array): #{

	global ttyCols, top_margin, left_margin, points, score, lives, level, board_rows, board_cols, save_top, save_left, stat_space, stat_rows

	set_topleft_ref(0,0)
						
	for rowi in range(board_rows + 1):	
		print('\033[u' + '\033[' + str(rowi) +  'B' + ''.join(board_array[rowi - 1]))		

	if (debug):
		print('\033[u' + '\033[' + str(len(board) + 4) + 'B' + '\r\033[0m\033[37mPlayer: ' + str(player) )
		for i in range(0, len(eggs)):
			if i == 0: print('\033[u' + '\033[' + str(len(board) + 6 + i) + 'B' + '\r\033[K\033[1B\033[K\033[1A\033[0m\033[37mEggs: ' + str(eggs[i]))
			else: print('\033[u' + '\033[' + str(len(board) + 6 + i) + 'B' + '\r\033[K\033[1B\033[K\033[1A\t\033[0m\033[37mEgg ' + str(i) + ': ' + str(eggs[i]))
		for i in range(0, len(beasts)):
			if i == 0: print('\033[u' + '\033[' + str(len(board) + len(eggs) + 7 + i) + 'B' + '\r\033[K\033[1B\033[K\033[1A\033[0m\033[37mBeasts: ' + str(beasts[i]))
			else: print('\033[u' + '\033[' + str(len(board) + len(eggs) + 7 + i) + 'B' + '\r\033[K\033[1B\033[K\033[1A\t\033[0m\033[37mBeast ' + str(i) + ': ' + str(beasts[i]))
		for i in range(0, len(monsters)):
			if i == 0: print('\033[u' + '\033[' + str(len(board) + len(eggs) + len(beasts) + 8 + i) + 'B' + '\r\033[K\033[1B\033[K\033[1A\033[0m\033[37mMonsters: ' + str(monsters[i]))
			else: print('\033[u' + '\033[' + str(len(board) + len(eggs) + len(beasts) + 8 + i) + 'B' + '\r\033[K\033[1B\033[K\033[1A\t\033[0m\033[37mMonster ' + str(i) + ': ' + str(monsters[i]))
		 
	print('\033[u\033[0m\033[37m\033[' + str(len(board) + 1) + 'B' + '\033[' + str(stat_space) + 'C' + '\033[s\033[2K' + chr(9477) + 
	' ' + 'TOTAL: ' + str(score)  + 	' ' + chr(9477) + '       \033[u\033[' + str((stat_space + 14) * 1) + 'C' + chr(9477) + 
	' ' + 'TALLY: ' + str(points) + 	' ' + chr(9477) + '\033[u\033[' + str((stat_space + 14) * 2) + 'C' + chr(9477) + 
	' ' + 'LIVES: ' + str(lives)  +  	' ' + chr(9477) + '\033[u\033[' + str((stat_space + 14) * 3) + 'C' + chr(9477) + 
	' ' + 'LEVEL: ' + str(level)  +  	' ' + chr(9477)) 

	print('\033[H\033[8m')

##########################################################################################################
##############################################################################-- play audio function --###
##########################################################################################################
def play_audio(filename): system('aplay -q audio/' + filename + '.wav &')

play_audio('menu_item_tick')

##########################################################################################################
###############################################################################-- place the pieces -- ####
##########################################################################################################
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
###########################################################################################
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
###########################################################################################################
########################################################################################-- EGGS --#########
###########################################################################################################
def lay_egg(row, col):
	
	global incubate, monsters, beasts, eggs, board, egg_speed, LCD_TIME
	
	enemy_total = len(eggs) + len(beasts) + len(monsters)
	eggs[0]['frames'] = (int(egg_speed / LCD_TIME))
	wait_frames = int(eggs[0]['incu_frames'] * (( enemy_total * incubate ) / 10) + randint(0, (2 * eggs[0]['incu_frames']))) # seconds of wait time before egg starts counting down 
	stag = randint(1, eggs[0]['frames']) # the frame that the egg counts down on
	board[row][col] = EGG(32)
	eggs.append({'ro': row, 'co': col, 'wait': wait_frames, 'stg': stag, 'sub':32})
##############################################################################################
def place_eggs(count):

	global board, BAKGRD

	step = 0 
	while(step < count):
		row = randint(1, (board_rows - 1))
		col = randint(1, (board_cols - 1))
		if(board[row][col] == BAKGRD):
			lay_egg(row, col)
			step += 1

#####################################################################
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
		elif (eggs[i - di]['wait'] == 0) & (eggs[i - di]['sub'] == 32):
			eggs[i - di]['sub'] = 8329
		elif (eggs[i - di]['wait'] == 0) :
			if ((eggs[i - di]['stg'] == eggs[0]['frame']) & (eggs[i - di]['sub'] > 8320)):
				eggs[i - di]['sub'] -= 1
				board[eggs[i - di]['ro']][eggs[i - di]['co']] = EGG(eggs[i - di]['sub'])
			elif ((eggs[i - di]['sub'] == 8320) & (eggs[i - di]['stg'] == eggs[0]['frame'])):
				hatch_monster(eggs[i - di]['ro'], eggs[i - di]['co'])
				del eggs[i - di]
				play_audio('hatch')
				di += 1
##############################################################################
###############################################-- move pieces --##############
##############################################################################
def flash_player():

	global player, PLAYER, plr_flashes, plr_flash, plr_frames, plr_frame

	neg_PLAYER = '\033[7m\033[34m\033[40m' + chr(9664) + chr(9654) + '\033[0m'
	pos_PLAYER = '\033[34m\033[40m' + chr(9664) + chr(9654) + '\033[0m'

	if plr_flash <= plr_flashes:
		if plr_frame < plr_frames:
			plr_frame += 1
		elif plr_frame == plr_frames:
			plr_frame = 0
			if board[player[1]['ro']][player[1]['co']] == PLAYER:
				board[player[1]['ro']][player[1]['co']] = neg_PLAYER
			else:
				board[player[1]['ro']][player[1]['co']] = PLAYER

			plr_flash += 1

	# if the flash is greater than 0
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
	plr_flash = 0

def kill_player():

	global BAKGRD, player, lives, board, timeout

	board[ player[1]['ro'] ][ player[1]['co'] ] = BAKGRD
	lives -= 1
	del player[1]
	if lives > 0:
		place_player()

	timeout += 1
		
	play_audio('death')

def move_enemies(pawns): #{

	global board, player, MOVES

	if pawns[0]['frame'] >= pawns[0]['frames']:
		pawns[0]['frame'] = 0
	else:
		pawns[0]['frame'] += 1

	move_priority = []
	move = ''
	breakloop = False
	#lay = False
	likely_moves = []

	for pwni in range(1, (len(pawns))): # in a given frame, loops through all pawns in a list if the pawn is staggered to move in the present frame, the pawn moves to a space
		if (pawns[pwni]['stg'] == pawns[0]['frame']):
			rdistance = player[1]['ro'] - pawns[pwni]['ro'] # player row minus beast row
			cdistance = player[1]['co'] - pawns[pwni]['co'] # player column minus beast column

			if (rdistance == 0) | (cdistance == 0): # avoid division by zero
				distance_ratio = 0.0 # if the player is on the same row or column, the distance ratio is zero
			else:
				distance_ratio = rdistance / cdistance # division of row distance by column distance

			if ((rdistance < 0.0) & (cdistance < 0.0) & (distance_ratio >= .5) & (distance_ratio <= 2.0)):
				move_priority = [ 'UL', 'U', 'L', 'DL', 'UR', 'D', 'R', 'DR' ] # UPPER LEFT range priorities
			elif ((rdistance < 0.0) & (cdistance > 0.0) & (distance_ratio <= -.5) & (distance_ratio >= -2.0)):
				move_priority = [ 'UR', 'U', 'R', 'UL', 'DR', 'L', 'D', 'DL' ] # UPPER RIGHT range priorities
			elif ((rdistance > 0.0) & (cdistance > 0.0) & (distance_ratio >= .5) & (distance_ratio <= 2.0)):
				move_priority = [ 'DR', 'D', 'R', 'DL', 'UR', 'U', 'L', 'UL' ] # DOWN RIGHT range priorities
			elif ((rdistance > 0.0) & (cdistance < 0.0) & (distance_ratio <= -.5) & (distance_ratio >= -2.0)):
				move_priority = [ 'DL', 'D', 'L', 'UL', 'DR', 'U', 'R', 'UR' ] # DOWN LEFT range priorities
			elif ((rdistance < 0.0) & ((abs(distance_ratio) > 2.0) | (distance_ratio == 0.0))):
				move_priority = [ 'U', 'UL', 'UR', 'L', 'R', 'DL', 'DR', 'D' ] # UPWARD range priorities
			elif ((cdistance > 0.0) & ((abs(distance_ratio) < .5) | (distance_ratio == 0.0))):
				move_priority = [ 'R', 'UR', 'DR', 'U', 'D', 'UL', 'DL', 'L' ] # RIGHT range priorities
			elif ((rdistance > 0.0) & ((abs(distance_ratio) > 2.0) | (distance_ratio == 0.0))):
				move_priority = [ 'D', 'DL', 'DR', 'L', 'R', 'UL', 'UR', 'U' ] # DOWNWARD range priorities
			elif ((cdistance < 0.0) & ((abs(distance_ratio) < .5) | (distance_ratio == 0.0))):
				move_priority = [ 'L', 'UL', 'DL', 'U', 'D', 'UR', 'DR', 'R' ] # LEFT range priorities

			priority_odds = [  #145 total
				[98, False],   #98		    ***********************************************
				[18, False],   #18 or 36	* These values determine the odds of moves    *
				[18, False],   #18 or 36	* for an enemy if those moves are available.  *
				[4, False],	   #4 or 8		* If a move is not unavailable, then its odds *
				[4, False],	   #4 or 8		* are absorbed: 1st by its equal counterpart, *
				[1, False],	   #1 or 2		* or 2nd, by the next lower priority, etc.    *
				[1, False],	   #1 or 2		*    THE WEIGHTS ARE DIFFICULT TO CHANGE      *	
				[1, False]	   #1		    ***********************************************
			]

			for priopti in range(8): 
				# if the first priority move is the player, then take that move (pawn kills player)
				if ((board[ ((pawns[pwni]['ro']) + (MOVES[move_priority[0]]['ra'])) ][ ((pawns[pwni]['co']) + (MOVES[move_priority[0]]['ca'])) ]) == PLAYER ):
					move = move_priority[0]
					board[pawns[pwni]['ro']][pawns[pwni]['co']] = BAKGRD
					pawns[pwni]['ro'] = player[1]['ro']
					pawns[pwni]['co'] = player[1]['co']
					kill_player()
					board[pawns[pwni]['ro']][pawns[pwni]['co']] = pawns[0]['chr']
					breakloop = True
					break
				# else if the priority move is not available, then mark it as unavailable
				elif ((board[ ((pawns[pwni]['ro']) + (MOVES[move_priority[priopti]]['ra'])) ][ ((pawns[pwni]['co']) + (MOVES[move_priority[priopti]]['ca'])) ]) == BAKGRD ):
					priority_odds[priopti][1] = True
				else:
					priority_odds[priopti][1] = False
					if ((pawns[0]['chr'] == MONSTER) & ((board[ ((pawns[pwni]['ro']) + (MOVES[move_priority[0]]['ra'])) ][ ((pawns[pwni]['co']) + (MOVES[move_priority[0]]['ca'])) ] == MONSTER) | (board[ ((pawns[pwni]['ro']) + (MOVES[move_priority[0]]['ra'])) ][ ((pawns[pwni]['co']) + (MOVES[move_priority[0]]['ca'])) ] == BEAST))):
						if (choices([True, False], [3, 127], k=1)) == [True]:
							place_eggs(1)
	
			for prioddi in range(8): # loop through priorities to add them to likely_moves if available
				if (priority_odds[prioddi][1] == True): # if it is true that the priority move is a blank space, then loop through and fill out the likely_moves list
					for ti in range(priority_odds[prioddi][0]): # loop through by number in "priorities" loop, to fill out likely_moves list
						likely_moves.append(move_priority[prioddi])
				if ((prioddi == 2) | (prioddi == 4) | (prioddi == 6)):
					if ((not priority_odds[prioddi - 1][1]) & (priority_odds[prioddi][1] == True)):
						for ti in range(priority_odds[prioddi][0]):
							likely_moves.append(move_priority[prioddi])

			# the move is finally decided out of the available set in the list
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

def push_tree(intent):

	global player, eggs, board, BLOCK, MOVES, BAKGRD, BOX, PLAYER

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
		if ((player[1]['tug']) & (board[tug_r][tug_c] == BOX)):
			board[tug_r][tug_c] = BAKGRD
			board[stnce_r][stnce_c] = BOX
		else:
			board[ player[1]['ro'] ][ player[1]['co'] ] = BAKGRD
		player[1]['ro'] = intend_r	
		player[1]['co'] = intend_c								# make player fol and fow the player
		board[intend_r][intend_c] = PLAYER						# move_player()
	
	def kill_enemy(pawns, row, col):

		global points, board

		del_index = 0

		for i in range(1, (len(pawns))):
			if ((pawns[i]['ro'] == row) & (pawns[i]['co'] == col)):
				del_index = i
				break
		del pawns[del_index]
		points += pawns[0]['pnts']

	probe = 2
	loop = True
	while (loop):

		space = board[probe_r(probe)][probe_c(probe)]
		ram_space = board[ram_r(probe)][ram_c(probe)]

		if (((probe_r(probe) != 0) & (probe_r(probe) != (len(board) - 1))) & ((probe_c(probe) != 0) & (probe_c(probe) != len(board[0]) - 1))):
			wall_space = board[wall_r(probe)][wall_c(probe)]
	
		if (space == BOX):		# if space is a box
			probe += 1 		# start loop over
		elif (space == BAKGRD): 		# if space is 
			push_move()
			loop = False
		elif (deteggt(space) == True): 	# if space is a egg
			if (wall_space == BLOCK) | (wall_space == KILLBLOCK):	# if next block after egg is a border
				kill_enemy(eggs, probe_r(probe), probe_c(probe)) 			# del egg from global egg list
				play_audio('hatch')
				push_move()
				loop = False						# make space same as preceeding space
#			elif ((wall_space == BAKGRD) | (wall_space == BOX)):
			else:
				for i in range(1, len(eggs)):
					if ((eggs[i]['ro'] == probe_r(probe)) & (eggs[i]['co'] == probe_c(probe))):
						push_eggs = [i] + push_eggs
				probe += 1
		elif (space == BLOCK):				# if space is a border
			loop = False
		elif (space == KILLBLOCK):	 		# if space is a killblock
			play_audio('flatten')
			push_move()
			board[probe_r(probe - 1)][probe_c(probe - 1)] = KILLBLOCK
			loop = False
		elif (space == BEAST): # if space is a beast
			if ((wall_space == KILLBLOCK) | (wall_space == BOX) | (wall_space == BLOCK)):
				kill_enemy(beasts, probe_r(probe), probe_c(probe))
				play_audio('squish')
				push_move()
			loop = False
		elif (space == MONSTER):# if space is a monster	
			if ((wall_space == KILLBLOCK) | (wall_space == BLOCK)):
				kill_enemy(monsters, probe_r(probe), probe_c(probe))
				play_audio('squish')
				push_move()		
			loop = False
			
		else:
			system('echo \"' + str(space) + '\" >> probe_space.txt')
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
	if (player[1]['tug']) & (board[rtug][ctug] == BOX):
		board[rtug][ctug] = BAKGRD
		board[row][col] = BOX
		if (pulling == 'hold'):
			player[1]['tug'] == False
	else:
		board[row][col] = BAKGRD
	player[1]['ro'] = fow
	player[1]['co'] = fol

def direct_move(tap_move):

	global player, MOVES, board

	space = board[player[1]['ro'] + MOVES[tap_move]['ra'] ][ player[1]['co'] + MOVES[tap_move]['ca'] ]

	if (space == BAKGRD):
		move_player(tap_move)
	elif (space == BOX):
		push_tree(tap_move)
	elif (space == MONSTER) | (space == BEAST) | (space == KILLBLOCK):
		kill_player()

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
	if (pulling == 'hold'):
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
######################################################################
########################-- question user about board-size --##########
######################################################################
def pause():

	global board_rows, board_cols, left_margin, top_margin

	play_audio('pause')

	pauseleft = (left_margin + board_cols - 8)
	pausetop = (top_margin + int(board_rows/4)) 
	print('\033[0m\033[40m')	
	print('\033[' + str(pausetop) + ';' + str(pauseleft) + 'H' + ' '*16)
	print('\033[' + str(pausetop + 1) + ';' + str(pauseleft) + 'H' + ' ' + chr(9556) + chr(9552)*12 + chr(9559) + ' ')
	print('\033[' + str(pausetop + 2) + ';' + str(pauseleft) + 'H' + ' ' + chr(9553) + '            ' + chr(9553) + ' ')
	print('\033[' + str(pausetop + 3) + ';' + str(pauseleft) + 'H' + ' ' + chr(9553) + '   PAUSED   ' + chr(9553) + ' ')
	print('\033[' + str(pausetop + 4) + ';' + str(pauseleft) + 'H' + ' ' + chr(9553) + '            ' + chr(9553) + ' ')
	print('\033[' + str(pausetop + 5) + ';' + str(pauseleft) + 'H' + ' ' + chr(9562) + chr(9552)*12 + chr(9565) + ' ')
	print('\033[' + str(pausetop + 6) + ';' + str(pauseleft) + 'H' + ' '*16)
	
	print('\033[H\033[0m')

	while(keypress == ord('p')):
		sleep(.08)

	play_audio('pause')
#####################################################################################################
#######################################################-- main function calls -######################
#####################################################################################################
def build_level():
	
	global incubate, egg_speed, beast_speed, monster_speed, keypress 
	global play_rows, play_cols, board_rows, board_cols, reset_board, blank_board 
	global board, level, lives, score, points, mi1_opt
	global lvl_block_cnt, lvl_beast_cnt, lvl_monster_cnt, lvl_egg_cnt, lvl_box_cnt, block_type
	global BAKGRD, BLOCK, KILLBLOCK, last_frame, top_margin, left_margin, LCD_TIME 
	global KEY_UP, KEY_DOWN, KEY_RIGHT, KEY_LEFT, KEY_P_UP, KEY_P_DOWN, KEY_P_LEFT, KEY_P_RIGHT, pulling

	stdscr = initscr() 
	stdscr.keypad(1)
	stdscr.refresh()

	block_type = BLOCK
	lvl_block_cnt = 10 
	lvl_beast_cnt = 0
	lvl_monster_cnt = 0
	lvl_egg_cnt = 0
	invisibleBEAST = '\033[30m\033[40m' + chr(9500) + chr(9508) + '\033[0m'
	print_board(board)
	sleep(.5)
	board = []
	board = build_the_board()
	print_board(board)

	if (level == 0):
		sleep(1)
		set_topmid_ref(3, 29)
		play_audio('begin')
		print('\033[u\033[2B' + invisibleBEAST + BEAST*4 + BAKGRD*2 + BEAST*5 + BAKGRD*3 + BEAST*1 + BAKGRD*4 + BEAST*3 + BAKGRD*2 + BEAST*5)
		print('\033[u\033[3B' + invisibleBEAST + BEAST*1 + BAKGRD*3 + BEAST*1 + BAKGRD*1 + BEAST*1 + BAKGRD*6 + BEAST*1 + BAKGRD*1 + BEAST*1 + BAKGRD*2 + BEAST*1 + BAKGRD*3 + BEAST*1 + BAKGRD*3 + BEAST*1)
		print('\033[u\033[4B' + invisibleBEAST + BEAST*1 + BAKGRD*3 + BEAST*1 + BAKGRD*1 + BEAST*1 + BAKGRD*5 + BEAST*1 + BAKGRD*3 + BEAST*1 + BAKGRD*1 + BEAST*1 + BAKGRD*7 + BEAST*1)
		print('\033[u\033[5B' + invisibleBEAST + BEAST*4 + BAKGRD*2 + BEAST*3 + BAKGRD*3 + BEAST*5 + BAKGRD*2 + BEAST*3 + BAKGRD*4 + BEAST*1)
		print('\033[u\033[6B' + invisibleBEAST + BEAST*1 + BAKGRD*3 + BEAST*1 + BAKGRD*1 + BEAST*1 + BAKGRD*5 + BEAST*1 + BAKGRD*3 + BEAST*1 + BAKGRD*5 + BEAST*1 + BAKGRD*3 + BEAST*1)
		print('\033[u\033[7B' + invisibleBEAST + BEAST*1 + BAKGRD*3 + BEAST*1 + BAKGRD*1 + BEAST*1 + BAKGRD*5 + BEAST*1 + BAKGRD*3 + BEAST*1 + BAKGRD*1 + BEAST*1 + BAKGRD*3 + BEAST*1 + BAKGRD*3 + BEAST*1)
		print('\033[u\033[8B' + invisibleBEAST + BEAST*4 + BAKGRD*2 + BEAST*5 + BAKGRD*1 + BEAST*1 + BAKGRD*3 + BEAST*1 + BAKGRD*2 + BEAST*3 + BAKGRD*4 + BEAST*1)
		set_cursor_avoid()
		sleep(.4)
		set_topmid_ref(17, 35)
		print('\033[37m\033[2m\033[40mPress the Spacebar to Play . . .\033[0m')
		set_cursor_avoid()
		while (keypress != ord(' ')):
			sleep(.2)

	set_topmid_ref(17, 35)
	print('\033[37m\033[2m\033[40mPress \033[36mtab \033[37mfor \033[35mSettings\033[30m . . .       \033[0m')
	sleep(1.2)

	if (lives == 0):
		score += points
		if level != 0: score -= 75
		level -= 3
		if level < 1: level = 1
		lives = 5
		points = 0
		
		for i in range(1, len(player)): del player[1]
		for i in range(1, len(beasts)): del beasts[1]
		for i in range(1, len(monsters)): del monsters[1]
		for i in range(1, len(eggs)): del eggs[1]
	else:
		level += 1
		score += points
		points = 0
		for i in range(1, len(player)): del player[1]

	def lvl_set(beas, mons, egs, blctp):
		global block_type, lvl_beast_cnt, lvl_monster_cnt, lvl_egg_cnt
		lvl_beast_cnt = beas
		lvl_monster_cnt = mons
		lvl_egg_cnt = egs
		block_type = blctp

	def lvl_set(beas, mons, egs, blctp):
		global lvl_beast_cnt, lvl_monster_cnt, lvl_egg_cnt, block_type
		lvl_beast_cnt = beas
		lvl_monster_cnt = mons
		lvl_egg_cnt = egs
		block_type = blctp

	if level == 1: lvl_set(3, 0, 0, BLOCK)
	elif level == 2: lvl_set(5, 0, 0, KILLBLOCK)
	elif level == 3: lvl_set(5, 0, 2, BLOCK)
	elif level == 4: lvl_set(4, 1, 1, KILLBLOCK)
	elif level == 5: lvl_set(4, 2, 2, BLOCK)
	elif level == 6: lvl_set(8, 0, 0, KILLBLOCK)
	elif level == 7: lvl_set(0, 0, 8, KILLBLOCK)
	elif level == 8: lvl_set(0, 8, 0, KILLBLOCK)
	elif level == 9: lvl_set(3, 3, 3, BLOCK)
	elif level == 10: lvl_set(2, 4, 3, BLOCK)
	elif level == 11: lvl_set(1, 5, 4, KILLBLOCK)
	elif level == 12: lvl_set(1, 6, 4, KILLBLOCK)
	elif level == 13: lvl_set(0, 0, 12, KILLBLOCK)
	elif level == 14: lvl_set(0, 12, 0, KILLBLOCK)
	elif level == 15: lvl_set(15, 0, 0, KILLBLOCK)
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

	lower_boxes = int(play_rows * play_cols / 4 - 10)
	upper_boxes = int(play_rows * play_cols / 4 + 10)
	lvl_box_cnt = randint(lower_boxes, upper_boxes)
	lvl_block_cnt = 10
	main_menu = 0
	item_menu = 0
	controls_menu = 9
	menu_ref = '\033[' + str(top_margin + 3) + ';' + str(left_margin + 6) + 'H\033[s\033[0m'
	dim = '\033[0m\033[40m\033[2m'
	norm = '\033[0m\033[40m'
	ltab = '\033[0m\033[7m\033[40m'
	dtab = '\033[0m\033[7m\033[40m\033[2m'
	speedbg = '\033[40m\033[34m|||\033[32m|||||\033[33m\033[31m||\033[37m\033[40m'
	speed_arrow = '\033[40m\033[35m' + chr(9632) + '\033[40m' # 10219 (thin double) 9193 (skip) 9670 (diamon)
	chr_cnt = 0
	mi1_shade = '' ###############-- item 1

	#mi1_opt = 2 # (set globally on line 52)
	mi2_shade = '' ###############-- item 2
	mi2_opt = 0
	if pulling == 'hold': mi2_opt = 1
	elif pulling == 'toggle': mi2_opt = 2
	elif pulling == 'single': mi2_opt = 3
	elif pulling == 'auto': mi2_opt = 4
	# pulling set globally on line 74
	toggle, single, auto = '', '', ''
	mi3_shade = '' ###############-- item 3
	mi4_shade = '' ###############-- item 4
	mi5_shade = '' ###############-- item 5
	mi6_shade = '' ###############-- item 6
	mi7_shade = '' ###############-- item 7
	mi8_shade = '' ###############-- item 8
	mi8_opt = 0
	if block_type == BLOCK: mi8_opt = 1
	elif block_type == KILLBLOCK: mi8_opt = 2
	normalyellow, dangerousorange = '', ''
	mi9_shade = '' ###############-- item 9
	beast_speed_min = .3
	beast_speed_max = 2.3
	beast_speed_inc = .2
	beast_speed = beast_speed - (beast_speed % beast_speed_inc)
	if (beast_speed > beast_speed_max): beast_speed = beast_speed_max
	elif (beast_speed < beast_speed_min): beast_speed = beast_speed_min
	beast_arrows = int((beast_speed - beast_speed_min ) / beast_speed_inc) 
	mi10_shade = '' ##############-- item 10
	monster_speed_min = .3
	monster_speed_max = 2.3
	monster_speed_inc = .2
	monster_speed = monster_speed - (monster_speed % monster_speed_inc)
	if (monster_speed > monster_speed_max): monster_speed = monster_speed_max
	elif (monster_speed < monster_speed_min): monster_speed = monster_speed_min
	monster_arrows = int((monster_speed - monster_speed_min) / monster_speed_inc)
	mi11_shade = '' ##############-- item 11
	incubate_min = 4
	incubate_max = 40
	incubate_inc = 4
	incubate = incubate - (incubate % incubate_inc)
	if (incubate > incubate_max): incubate = incubate_max
	elif (incubate < incubate_min): incubate = incubate_min
	incubate_arrows = int((incubate - incubate_min) / incubate_inc)
	mi12_shade = '' ##############-- item 12
	timer_min = .5
	timer_max = 5
	timer_inc = .5
	egg_speed = egg_speed - (egg_speed % timer_inc)
	if (egg_speed > timer_max): egg_speed = timer_max
	elif (egg_speed < timer_min): egg_speed = timer_min
	timer_arrows = int((egg_speed - timer_min) / timer_inc) 

	def dim_menus(mi):
		global mi1_shade, mi2_shade, mi3_shade, mi4_shade, mi5_shade, mi6_shade, mi7_shade, mi8_shade, mi9_shade, mi10_shade, mi11_shade, mi12_shade
		if mi != 1: mi1_shade = dim ##############-- item 1
		else: mi1_shade = norm
		if mi != 2: mi2_shade = dim ##############-- item 2
		else: mi2_shade = norm
		if mi != 3: mi3_shade = dim ##############-- item 3
		else: mi3_shade = norm
		if mi != 4: mi4_shade = dim ##############-- item 4
		else: mi4_shade = norm
		if mi != 5: mi5_shade = dim ##############-- item 5
		else: mi5_shade = norm
		if mi != 6: mi6_shade = dim ##############-- item 6
		else: mi6_shade = norm
		if mi != 7: mi7_shade = dim ##############-- item 7
		else: mi7_shade = norm
		if mi != 8: mi8_shade = dim ##############-- item 8
		else: mi8_shade = norm
		if mi != 9: mi9_shade = dim ##############-- item 9
		else: mi9_shade = norm
		if mi != 10: mi10_shade = dim ##############-- item 10
		else: mi10_shade = norm
		if mi != 11: mi11_shade = dim ##############-- item 11
		else: mi11_shade = norm
		if mi != 12: mi12_shade = dim ##############-- item 12
		else: mi12_shade = norm
	def main_menu_1():
		global mi1_opt, mi1_shade, mi2_shade, wasd, arrows, vi, pulling, single, toggle, auto

		print('\033[u\033[3B' + mi1_shade + 'Movement Keys: ' + wasd + mi1_shade + arrows + mi1_shade + vi)
		print('\033[u\033[5B' + mi2_shade + 'Pulling Boxes: ' + hold + mi2_shade + toggle + mi2_shade + single + mi2_shade + auto)
		
		pullkey = ''
		if (pulling == 'hold'): pullkey = 'Shift   '
		else: pullkey = 'Spacebar'
			
		print('\033[u\033[8B\033[0m\033[40m\033[37m\033[2m' + ' '*32 + 'Block-Pull Key: \033[36m' + pullkey + ' \033[0m')
		print('\033[u\033[15B\033[0m\033[40m\033[37m\033[2mPress \033[36mESC \033[37mto enter the game')
		print('\033[u\033[16B\033[0m\033[40m\033[37m\033[2mPress \033[36mTab \033[37mto switch menu tabs\033[0m')	

	def main_menu_2():
		global mi3_shade, mi4_shade, mi5_shade, mi6_shade, mi7_shade, mi8_shade, BLOCK, block_type, KILLBLOCK, normalyellow, dangerousorange,  play_rows, play_cols
		#global lvl_block_cnt, lvl_box_cnt, lvl_beast_cnt, lvl_monster_cnt, lvl_egg_cnt,
		global lvl_beast_cnt, lvl_monster_cnt, lvl_egg_cnt
		print('\033[u\033[4B\033[34C' + dim + 'Total Spaces: \033[36m' + str(play_rows * play_cols) + ' \033[37m')
		print('\033[u\033[5B\033[35C' + dim + 'Used Spaces: \033[36m' + str(lvl_box_cnt + lvl_block_cnt + lvl_monster_cnt + lvl_beast_cnt + lvl_egg_cnt) + ' \033[37m')
		print('\033[u\033[6B\033[35C' + dim + 'Free Spaces: \033[36m' + str((play_rows * play_cols) - (lvl_block_cnt + lvl_box_cnt + lvl_monster_cnt + lvl_beast_cnt + lvl_egg_cnt)) + ' \033[37m')

		print('\033[u\033[3B' + mi3_shade + BEAST + mi3_shade + '\033[40m - Beast Count: \033[35m' + str(lvl_beast_cnt) + ' \033[37m')
		print('\033[u\033[5B' + mi4_shade + MONSTER + mi4_shade + '\033[40m - Monster Count: \033[35m' + str(lvl_monster_cnt) + ' \033[37m')
		print('\033[u\033[7B' + mi5_shade + EGG(32) + mi5_shade + '\033[40m - Egg Count: \033[35m' + str(lvl_egg_cnt) + ' \033[37m')
		print('\033[u\033[9B' + mi6_shade + BOX + mi6_shade + '\033[40m - Box Count: \033[35m' + str(lvl_box_cnt) + ' \033[37m')
		print('\033[u\033[11B' + mi7_shade + block_type + mi7_shade + '\033[40m - Block Count: \033[35m' + str(lvl_block_cnt) + ' \033[37m')
		print('\033[u\033[13B' + mi8_shade + block_type + mi8_shade + '\033[40m - Block Type: ' + normalyellow + mi8_shade + dangerousorange + mi8_shade + ' \033[37m')

	def main_menu_3():
		global mi9_shade, mi10_shade, mi11_shade, mi12_shade, incubate
		print('\033[u\033[3B' + mi9_shade + BEAST + mi9_shade +        ' - Beast:           slower ' + speedbg + ' faster\033[' + str(beast_arrows + 8) +    'D' + speed_arrow + '\033[30m')
		print('\033[u\033[5B' + mi10_shade + MONSTER + mi10_shade +    ' - Monster:         slower ' + speedbg + ' faster\033[' + str(monster_arrows + 8) +  'D' + speed_arrow + '\033[30m')
		print('\033[u\033[7B' + mi11_shade + EGG(32) + mi11_shade +    ' - Egg Incubate:    slower ' + speedbg + ' faster\033[' + str(incubate_arrows + 8) + 'D' + speed_arrow + '\033[30m')
		print('\033[u\033[9B' + mi12_shade + EGG(8320) + mi12_shade +  ' - Egg Timer:       slower ' + speedbg + ' faster\033[' + str(timer_arrows + 8) +    'D' + speed_arrow + '\033[30m')

	def mi1_controls(opt):
		global KEY_UP, KEY_DOWN, KEY_RIGHT, KEY_LEFT, KEY_P_UP, KEY_P_DOWN, KEY_P_LEFT, KEY_P_RIGHT, wasd, arrows, vi, pulling
		if opt == 1:
			wasd = '[\033[35m w,a,s,d \033[37m]'
			arrows = '  arrows  '
			vi = '  h,j,k,l  '
			KEY_UP = 119
			KEY_DOWN = 115
			KEY_RIGHT = 100
			KEY_LEFT = 97
			KEY_P_UP = 87
			KEY_P_DOWN = 83
			KEY_P_RIGHT = 68
			KEY_P_LEFT = 65
		elif opt == 2:
			wasd = '  w,a,s,d  '
			arrows = '[\033[35m arrows \33[37m]'
			vi = '  h,j,k,l  '
			KEY_UP = 259
			KEY_DOWN = 258
			KEY_RIGHT = 261
			KEY_LEFT = 260
			KEY_P_UP = 337
			KEY_P_DOWN = 336
			KEY_P_RIGHT = 402
			KEY_P_LEFT = 393
		elif opt == 3:
			wasd = '  w,a,s,d  '
			arrows = '  arrows  '
			vi = '[\033[35m h,j,k,l \033[37m]'
			KEY_UP = 107
			KEY_DOWN = 106
			KEY_RIGHT = 108
			KEY_LEFT = 104
			KEY_P_UP = 75
			KEY_P_DOWN = 74
			KEY_P_RIGHT = 76
			KEY_P_LEFT = 72

	def mi2_controls(opt):
		global pulling, toggle, single, auto, hold 
		
		if opt == 1:
			pulling = 'hold'
			hold = '[\033[35m hold \033[37m]'
			toggle = '  toggle  '
			single = '  single  '
			auto = '  auto  '
		if opt == 2:
			pulling = 'toggle'
			hold = '  hold  '
			toggle = '[\033[35m toggle \033[37m]'
			single = '  single  '
			auto = '  auto  '
		elif opt == 3:
			pulling = 'single'
			hold = '  hold  '
			toggle = '  toggle  '
			single = '[\033[35m single \033[37m]'
			auto = '  auto  '
		elif opt == 4:
			pulling = 'auto' 
			hold = '  hold  '
			toggle = '  toggle  '
			single = '  single  '
			auto = '[\033[35m auto \033[37m]'

	def mi8_controls(opt):
		global block_type, BLOCK, KILLBLOCK, normalyellow, dangerousorange
		
		if opt == 1:
			block_type = BLOCK
			normalyellow = '[\033[35m Normal Yellow \033[37m]'
			dangerousorange = '  Dangerous Orange  '
		elif opt == 2:
			block_type = KILLBLOCK
			normalyellow = '  Normal Yellow  '
			dangerousorange = '[\033[35m Dangerous Orange \033[37m]'

	dim_menus(0)
	mi1_controls(mi1_opt)
	mi2_controls(mi2_opt)
	mi8_controls(mi8_opt)
	if keypress == 9:
		system('clear')
		print_board(blank_board)
		sleep(1.5)
		keypress == 999
		print_board(blank_board)
		print(menu_ref)
		while (True):############################################################
			if keypress == 9: ###############################################
				keypress = ''
				main_menu += 1
				play_audio('menu_tab')
				if main_menu > 3:
					main_menu = 1
				if main_menu == 1:
					print_board(blank_board)
					item_menu = 0
					dim_menus(0)
					print(menu_ref)
					print('\033[u' + norm + chr(9473) 
						+ dtab + ' key options ' + norm + chr(9473) 
						+ dtab + ' level setup ' + norm + chr(9473) 
						+ dtab + ' pawn speeds ' + norm + chr(9473)*20)
					sleep(.08)
					print('\033[u' + norm + chr(9473) 
						+ ltab + ' key options ' + norm + chr(9473) 
						+ dtab + ' level setup ' + norm + chr(9473) 
						+ dtab + ' pawn speeds ' + norm + chr(9473)*20)
				elif main_menu == 2:
					print_board(blank_board)
					item_menu = 2
					dim_menus(2)
					print(menu_ref)
					print('\033[u' + norm + chr(9473) 
						+ dtab + ' key options ' + norm + chr(9473) 
						+ dtab + ' level setup ' + norm + chr(9473) 
						+ dtab + ' pawn speeds ' + norm + chr(9473)*20)
					sleep(.08)
					print('\033[u' + norm + chr(9473) 
						+ dtab + ' key options ' + norm + chr(9473) 
						+ ltab + ' level setup ' + norm + chr(9473) 
						+ dtab + ' pawn speeds ' + norm + chr(9473)*20)
				elif main_menu == 3:
					print_board(blank_board)
					item_menu = 8
					dim_menus(8)
					print(menu_ref)
					print('\033[u' + norm + chr(9473) 
						+ dtab + ' key options ' + norm + chr(9473) 
						+ dtab + ' level setup ' + norm + chr(9473) 
						+ dtab + ' pawn speeds ' + norm + chr(9473)*20)
					sleep(.08)
					print('\033[u' + norm + chr(9473) 
						+ dtab + ' key options ' + norm + chr(9473) 
						+ dtab + ' level setup ' + norm + chr(9473) 
						+ ltab + ' pawn speeds ' + norm + chr(9473)*20)
			if main_menu == 1:
				main_menu_1()
				set_cursor_avoid()
			elif main_menu == 2:
				main_menu_2()
				set_cursor_avoid()
			elif main_menu == 3:
				main_menu_3()
				set_cursor_avoid()

			if ((keypress == KEY_UP) | (keypress == KEY_DOWN)):		
				if (main_menu == 1):
				
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
				elif (main_menu == 2):
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
				elif (main_menu == 3):
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
			elif ((keypress == KEY_LEFT) | (keypress == KEY_RIGHT)):
				maxed_cnt = (play_rows * play_cols) - (lvl_block_cnt + lvl_box_cnt + lvl_monster_cnt + lvl_beast_cnt + lvl_egg_cnt)
				if (main_menu == 1) & (item_menu == 1):
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
				elif (main_menu == 1) & (item_menu == 2):
					if (keypress == KEY_LEFT):
						mi2_opt -= 1
						if mi2_opt < 1: mi2_opt = 4
					elif (keypress == KEY_RIGHT):
						mi2_opt += 1
						if mi2_opt > 4: mi2_opt = 1
					if mi2_opt == 1: mi2_controls(1)
					elif mi2_opt == 2: mi2_controls(2)
					elif mi2_opt == 3: mi2_controls(3)
					elif mi2_opt == 4: mi2_controls(4)
					if item_menu != 3: play_audio('menu_item_tick')
					keypress = 999
							
				elif (main_menu == 2) & (item_menu == 3):
					if (keypress == KEY_LEFT):
						lvl_beast_cnt -= 1
						if lvl_beast_cnt < 0: 
							lvl_beast_cnt = 0
							play_audio('outofrange')
						else:
							play_audio('menu_item_tick')
					elif (keypress == KEY_RIGHT):
						lvl_beast_cnt += 1
						if lvl_beast_cnt > maxed_cnt: 
							lvl_beast_cnt = maxed_cnt
							play_audio('outofrange')
						else:
							play_audio('menu_item_tick')
					keypress = 999
				elif (main_menu == 2) & (item_menu == 4):
					if (keypress == KEY_LEFT):
						lvl_monster_cnt -= 1
						if lvl_monster_cnt < 0: 
							lvl_monster_cnt = 0
							play_audio('outofrange')
						else:
							play_audio('menu_item_tick')
					elif (keypress == KEY_RIGHT):
						lvl_monster_cnt += 1
						if lvl_monster_cnt > maxed_cnt: 
							lvl_monster_cnt = maxed_cnt
							play_audio('outofrange')
						else:
							play_audio('menu_item_tick')
					keypress = 999
				elif (main_menu == 2) & (item_menu == 5):
					if (keypress == KEY_LEFT):
						lvl_egg_cnt -= 1
						if lvl_egg_cnt < 0: 
							lvl_egg_cnt = 0
							play_audio('outofrange')
						else:
							play_audio('menu_item_tick')
					elif (keypress == KEY_RIGHT):
						lvl_egg_cnt += 1
						if lvl_egg_cnt > maxed_cnt: 
							lvl_egg_cnt = maxed_cnt
							play_audio('outofrange')
						else:
							play_audio('menu_item_tick')
					keypress = 999
				elif (main_menu == 2) & (item_menu == 6):
					if (keypress == KEY_LEFT):
						lvl_box_cnt -= 1
						if lvl_box_cnt < 0: 
							lvl_box_cnt = 0
							play_audio('outofrange')
						else:
							play_audio('menu_item_tick')
					elif (keypress == KEY_RIGHT):
						lvl_box_cnt += 1
						if lvl_box_cnt > maxed_cnt: 
							lvl_box_cnt = maxed_cnt
							play_audio('outofrange')
						else:
							play_audio('menu_item_tick')
					keypress = 999
				elif (main_menu == 2) & (item_menu == 7):
					if (keypress == KEY_LEFT):
						lvl_block_cnt -= 1
						if lvl_block_cnt < 0: 
							lvl_block_cnt = 0
							play_audio('outofrange')
						else:
							play_audio('menu_item_tick')
					elif (keypress == KEY_RIGHT):
						lvl_block_cnt += 1
						if lvl_block_cnt > maxed_cnt: 
							lvl_block_cnt = maxed_cnt
							play_audio('outofrange')
						else:
							play_audio('menu_item_tick')
					keypress = 999
				elif (main_menu == 2) & (item_menu == 8):
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
				elif (main_menu == 3) & (item_menu == 9):
					if (keypress == KEY_RIGHT):
						beast_speed -= beast_speed_inc
						if beast_speed < beast_speed_min:
							beast_speed = beast_speed_min
							play_audio('outofrange')
						else:
							play_audio('menu_item_tick')
					elif (keypress == KEY_LEFT):
						beast_speed += beast_speed_inc
						if beast_speed > beast_speed_max:
							beast_speed = beast_speed_max
							play_audio('outofrange')
						else:
							play_audio('menu_item_tick')
					beast_arrows = int((beast_speed - beast_speed_min ) / beast_speed_inc) 
					keypress = 999
				elif (main_menu == 3) & (item_menu == 10):
					if (keypress == KEY_RIGHT):
						monster_speed -= monster_speed_inc
						if monster_speed < monster_speed_min:
							monster_speed = monster_speed_min
							play_audio('outofrange')
						else:
							play_audio('menu_item_tick')
					elif (keypress == KEY_LEFT):
						monster_speed += monster_speed_inc
						if monster_speed > monster_speed_max:
							monster_speed = monster_speed_max
							play_audio('outofrange')
						else:
							play_audio('menu_item_tick')
					monster_arrows = int((monster_speed - monster_speed_min ) / monster_speed_inc) 
					keypress = 999
				elif (main_menu == 3) & (item_menu == 11):
					if (keypress == KEY_RIGHT):
						incubate -= incubate_inc
						if incubate < incubate_min:
							incubate = incubate_min
							play_audio('outofrange')
						else:
							play_audio('menu_item_tick')
					elif (keypress == KEY_LEFT):
						incubate += incubate_inc
						if incubate > incubate_max:
							incubate = incubate_max
							play_audio('outofrange')
						else:
							play_audio('menu_item_tick')
					incubate_arrows = int((incubate - incubate_min ) / incubate_inc) 
					keypress = 999
				elif (main_menu == 3) & (item_menu == 12):
					if (keypress == KEY_RIGHT):
						egg_speed -= timer_inc
						if egg_speed < timer_min:
							egg_speed = timer_min
							play_audio('outofrange')
						else:
							play_audio('menu_item_tick')
					elif (keypress == KEY_LEFT):
						egg_speed += timer_inc
						if egg_speed > timer_max:
							egg_speed = timer_max
							play_audio('outofrange')
						else:
							play_audio('menu_item_tick')
					timer_arrows = int((egg_speed - timer_min ) / timer_inc)
					keypress = 999

			if keypress == 27:
				keypress = ''
				print_board(blank_board)
				sleep(1)
				break
			sleep(LCD_TIME)			

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
	
	last_frame = 1

	play_audio('begin')
####################################################################################################
#########################################################################-- take input func -- #####
####################################################################################################
def take_input():

	global pulling, stdscr, debug, keypress, player, top_margin, left_margin, save_top, save_left, key_move, timeout, game_play_mode

	stdscr = initscr() 
	stdscr.keypad(1)
	
	while(True):
		sleep(LCD_TIME - .02)
		keypress = stdscr.getch()
		timeout = 0
		if (game_play_mode):
			if keypress == 27: # the esc key
				system('reset')
				exit()
			elif keypress == ord('r'):
				keypress = 999
				plan_the_board()
				system('clear')
			elif keypress == ord('b'):
				if debug == True:
					debug = False
					top_margin = save_top
					left_margin = save_left
					system('clear')
				else:
					debug = True
					top_margin = 0
					left_margin = 0
					system('clear')
			elif keypress == ord('p'):
				keypress = stdscr.getch()
				keypress = ''
			if pulling == 'auto':
				if keypress == ord(' '):
					while (keypress == ord(' ')):
						keypress = stdscr.getch()
						player[1]['tug'] = not player[1]['tug']
						if (keypress != ord(' ')):
							tugspan = keypress # logs the present direction to compare for direction change
							while (tugspan == keypress): # this ensures the player has pull function until direction key changes.
								direct_keypress(keypress)
								player[1]['tug'] = True
								keypress = stdscr.getch()				
				if keypress != ord(' '):
					player[1]['tug'] = False
					direct_keypress(keypress)
			elif pulling == 'hold':
				direct_keypress(keypress)
			elif pulling == 'toggle':
				if keypress == ord(' '):
					player[1]['tug'] = not player[1]['tug']
				direct_keypress(keypress)
			elif pulling == 'single':
				if keypress == ord(' '):
					while (keypress == ord(' ')):
						keypress = stdscr.getch()
						player[1]['tug'] = True
					direct_keypress(keypress)
				else:
					player[1]['tug'] = False
					direct_keypress(keypress)

system('reset')
plan_the_board()
############################################################################################################
Thread(target=take_input).start()  ###############-- the main game clock and print loop --#####
last_frame = 1

while(True):
	if timeout > 2:
		keypress = ord('p')
		timeout = 0
	if keypress == 27:
		system('reset')
		exit()
	elif keypress == ord('p'):
		pause()
	else:
		if ((lives == 0) | ((len(beasts) == 1) & (len(monsters) == 1) & (len(eggs) == 1))):
			if last_frame == 0:
				game_play_mode = False
				if lives == 0: play_audio('loss')
				elif level != 0: play_audio('win')
				build_level()	
				game_play_mode = True							
			last_frame -= 1
		move_enemies(beasts)
		move_enemies(monsters)
		hatch_eggs()
		flash_player()
		print_board(board)
	sleep(LCD_TIME)
################################################
input()
