import curses
from random import randint
from os import system, popen
from time import sleep
import threading
import re
#################################
#####-- get tty sizes --#########################
#############################################################
ttyRows, ttyCols = popen('stty size', 'r').read().split()######
ttyRows = int(ttyRows)################################################
ttyCols = int(ttyCols)###################################################
screen_rows = ttyRows########################################################
screen_cols = int(ttyCols / 2)#####################-- global settings --#####
#############################################################################

##################################-- tty dynamic board size settings 

max_play_rows = 40 	# alter max game height here
max_play_cols = 80 	# alter max game width here
max_beast_cnt = 10	# alter max beasts here

##################################-- starting game statistics

beast_cnt = 4 		# starting beasts	
lives = 5		# starting lives

squish_boxes = False	# boxes shuv into nothing against blocks
block_hit_death = False	# player dies when hitting blocks

##################################-- game scoring balance

level_scr = -50		# point loss if player loses level
beast_scr = 2		# points for killing beasts
egg_scr = 4		# points for killing eggs
monster_scr = 6		# points for killing monsters
death_scr = -10		# point loss for dying

##################################-- game time parameters
# framerate of the whole game
# best results between .05 and .08
# settings may have varied results between terminal and console
# settings may have varied results with OS screen refresh
# to check Ubuntu screen refresh in hz (refreshes per second), type 'xrandr' in terminal
# 1 (second) / 60.02 = ~.01666111... ???? not sure whether it makes a difference.
lcd_time = .03

###############################

beast_speed = 1.3	# seconds between enemy moves
monster_speed = 1.3	# seconds between enemy moves
egg_speed = 4		# seconds between countdowns



		# frame-rate of entire game (CODISTADIT)

####################################-- pawn move constants

MOVES = {
'U': {	'di':'U', 	'ra':-1, 	'ca':0, 	'mm':-1},
'D': {	'di':'D', 	'ra':1, 	'ca':0, 	'mm':1},
'L': {	'di':'L', 	'ra':0, 	'ca':-1, 	'mm':-1},
'R': {	'di':'R',	'ra':0, 	'ca':1, 	'mm':1},
'UL': {	'di':'UL',	'ra':-1, 	'ca':-1},
'UR': {	'di':'UR', 	'ra':-1, 	'ca':1},
'DL': {	'di':'DL', 	'ra':1, 	'ca':-1},
'DR': {	'di':'DR', 	'ra':1, 	'ca':1}
}

MVU = 'U'
MVD = 'D'
MVL = 'L'
MVR = 'R'
MVUL = 'UL'
MVUR = 'UR'
MVDL = 'DL'
MVDR = 'DR'

DIR_LIS = (MVU, MVD, MVL, MVR, MVUL, MVUR, MVDL, MVDR)

keypress = '' 

##################################-- formatted character constants


# (ANSI styles)	 FG   + 	BG   + 		Style +		Characters +			Reset
BAKGRD = 							'  ' 
BLOCK =		       		'\033[43m' +	       		'  ' + 				'\033[0m'
KILLBLOCK = 	'\033[31m'	'\033[43m' + 			chr(9618) + chr(9618) + 	'\033[0m'
BOX = 		'\033[32m' +					chr(9618) + chr(9618) +		'\033[0m'
XPBOX = 	'\033[32m' + 			'\033[2m' +	chr(9618) + chr(9618) + 	'\033[0m'
BEAST = 	'\033[31m' +					chr(9500) + chr(9508) +		'\033[0m'
MONSTER = 	'\033[31m' +					chr(9567) + chr(9569) +		'\033[0m'
PLAYER = 	'\033[34m' +					chr(9664) + chr(9654) +		'\033[0m'
# http://wiki.bash-hackers.org/scripting/terminalcodes

eggsub = 8329			# unicode key for subscript 9 (8328 = 8, and so on)
egg2nd = 32			# unicode key for a space character 
REGGX = re.compile('\u2B2C.') 	# use re.match(REGGX, char) to see if a piece is an egg

def EGG(sub):
	return '\033[37m\033[2m' + chr(11052) + '\033[1m' + chr(sub) + '\033[0m'


###################################-- Pawn Classes (Dictionaries)
##################################-- Pawn Lists 

# pawn lists dynamically grows and shrink with 

beasts = [{
	'frames': ((int(beast_speed / lcd_time)) - 1),
	'frame':0,
	'chr': BEAST,
	'pnts': 2 
	}]

monsters = [{
	'frames': ((int(monster_speed / lcd_time)) - 1),
	'frame':0,
	'chr': MONSTER,
	'pnts': 6
	}]

eggs = [{
	'frames': ((int(egg_speed / lcd_time)) - 1),
	'frame':0,
	'incu_frames': (int(1 / lcd_time)), # incu_frames add up to 1 second
	'incu_frame': 0,
	'pnts': 4
	}]

# 'sub'		updated digital unicode reference to subscript character
# 'wait'	randomized wait time before hatching countdown
player = [{
		'chr': PLAYER,
		'pnts': 10 
	}]
	
# 'push'
# 'tug'
# 'ro'		row
# 'co'		col
# 'fow'		potential move
# 'fol'		potential move
# 'mv'		direction of travel
# 'stag'	individual frame
################################################################################################
####################################################################-- level 1 setup --#########
################################################################################################

monster_cnt = 0	# level 1 count
egg_cnt = 0	# level 1 count

kills = 0	# changes in-game
level = 1	# change in order to start on a specific level
score = 0	# in-game total score
points = 0	# in-game level points added at end of level







################################################################################################
board = [] #########################################################-- board setup --###########
################################################################################################

######################################-- classic board size variables

play_rows = 20	# only change this in-game
play_cols = 40	# only change this in-game

block_cnt = 10	# level 1 count

######################################-- dynamic board dimensions

left_margin = 0 
top_margin = 0
max_play_rows = int(max_play_rows / 3) * int(3)
max_play_cols = int(max_play_cols / 3) * int(3)
min_play_rows = 9
min_play_cols = 9
board_rows = play_rows + 2
board_cols = play_cols + 2
debug = False

def plan_the_board(): #{

	global save_top, save_left, top_margin, left_margin, board_rows, board_cols, play_rows, play_cols, min_play_rows, min_play_cols, max_play_rows, max_play_cols, stat_rows, ttyCols, screen_rows, screen_cols

	padding = 2 # the blank border around a board
	fill_margin = 2 + padding # This prevents fill boards from completely removing margins
	stat_rows = 2
	used_rows = 0
	used_cols = 0

	if (classic_board):
		top_margin = int((screen_rows - board_rows - stat_rows) / 2)
		left_margin = int((ttyCols - board_cols*2) / 2)
	else:
		# this condition tests to see if the board is in the middle range of the fill size
		# if it is true, then the board should fill the terminal, but have a slim boarder
		if ((screen_rows <= (max_play_rows + fill_margin)) & (screen_rows > (min_play_rows + fill_margin))):
			play_rows = int((screen_rows - fill_margin - stat_rows) / 3) * int(3)
			if (play_rows > max_play_rows):
				play_rows = max_play_rows
			board_rows = play_rows + 2
			used_rows = board_rows + stat_rows
			top_margin = int((screen_rows - used_rows) / 2)
		else: # if the board is either small or huge 
			play_rows = int((screen_rows - padding - stat_rows) / 3) * int(3)
			if (play_rows > max_play_rows):
				play_rows = max_play_rows
			board_rows = play_rows + 2
			used_rows = board_rows + stat_rows
			top_margin = int((screen_rows - used_rows) / 2)

		if ((screen_cols <= (max_play_cols + fill_margin)) & (screen_cols > (min_play_cols + fill_margin))):
			play_cols = (int((screen_cols - fill_margin) / 3) * (int(3)))
			if (play_cols > max_play_cols):
				play_cols = max_play_cols
			board_cols = play_cols + 2
			left_margin = int((ttyCols - (board_cols * 2)) / 2)
		else: # if the board is either small or huge 
			play_cols = int((screen_cols - padding) / 3) * int(3)
			if (play_cols > max_play_cols):
				play_cols = max_play_cols
			board_cols = play_rows + 2
			left_margin = int((ttyCols - board_cols * 2) / 2)


	save_top = top_margin 
	save_left = left_margin
	#}

	

# BUILDS a blank board
def build_the_board(): #{
	global board_cols, board_rows, board

	for rowi in range(board_rows): # builds the board based on 'board_rows' and 'board_cols' which includes room for borders
		board.append([])
		for coli in range(board_cols):
			board[rowi].append([])
			board[rowi][coli] = BAKGRD

	for rowi in range(board_rows): # draws the game boarders on the board
		for coli in range(board_cols):
			if(rowi == 0) | (rowi == (board_rows - 1)) | (coli == 0) | (coli == (board_cols - 1)):
				board[rowi][coli] = BLOCK


#	intro = board
#	roster = board
#	controls = board
#	info = board
#
#	global intro, roster, controls, info

#}



def print_board(board_array, stats): #{

	global ttyCols, top_margin, left_margin, score, lives, level, board_rows, board_cols, save_top, save_left

	print('\033[?25l\033[0m\033[' + str(top_margin)  + ';' + str(left_margin) + 'H\033[s')
						
	for rowi in range(board_rows + 1):	
		print('\033[u' + '\033[' + str(rowi) +  'B' + ''.join(board_array[rowi - 1]))		
	
	if (stats):
		print('\033[u' + '\033[' + str(len(board) + 2) + 'B' + '   SCORE: ' + str(score) + '   LIVES: ' + str(lives) + '    LEVEL: ' + str(level)) 

	if (debug):
		print('\033[u' + '\033[' + str(len(board) + 4) + 'B' + '\rPlayer: ' + str(player) )
		for i in range(0, len(eggs)):
			if i == 0: print('\033[u' + '\033[' + str(len(board) + 6 + i) + 'B' + '\rEggs: ' + str(eggs[i]))
			else: print('\033[u' + '\033[' + str(len(board) + 6 + i) + 'B' + '\r\tEgg ' + str(i) + ': ' + str(eggs[i]))

		for i in range(0, len(beasts)):
			if i == 0: print('\033[u' + '\033[' + str(len(board) + len(eggs) + 7 + i) + 'B' + '\rBeasts: ' + str(beasts[i]))
			else: print('\033[u' + '\033[' + str(len(board) + len(eggs) + 7 + i) + 'B' + '\r\tBeast ' + str(i) + ': ' + str(beasts[i]))
		for i in range(0, len(monsters)):
			if i == 0: print('\033[u' + '\033[' + str(len(board) + len(eggs) + len(beasts) + 8 + i) + 'B' + '\rMonsters: ' + str(monsters[i]))
			else: print('\033[u' + '\033[' + str(len(board) + len(eggs) + len(beasts) + 8 + i) + 'B' + '\r\tMonster ' + str(i) + ': ' + str(monsters[i]))
		 
	print('\033[H')



###############################################################
####################################--block_cnt--##############
###############################################################

def place_randomly(char, count):

	step = 1	

	while(step < count):
		row = randint(1, (board_rows - 1))
		col = randint(1, (board_cols - 1))
		if(board[row][col] == BAKGRD):
			board[row][col] = char
		step += 1	





# fills the board with appropriate number of yellow block_cnt
def place_blocks(blocks): #{

	global play_rows, play_cols

	row_ranges = []
	col_ranges = []

	rowi = 0
	coli = 0

	if(classic_board):
		row_ranges = [[1,2],[3,4],[5,6],[7,8],[9,10],[11,12],[13,14],[15,16],[17,18],[19,20]]
		col_ranges = [[1,4],[5,8],[9,12],[13,16],[17,20],[21,24],[25,28],[29,32],[33,36],[37,40]]
		step = 9 
		rowi = 0
		coli = 0
		while(step >= 0):
			row_range_index = randint(0, step)
			rowi = randint(row_ranges[row_range_index][0], row_ranges[row_range_index][1])
			col_range_index = randint(0, step)
			coli = randint(col_ranges[col_range_index][0], col_ranges[col_range_index][1])
			board[rowi][coli] = blocks
			step -= 1
			del col_ranges[col_range_index]
			del row_ranges[row_range_index]
	else:
		block_cnt = round(play_rows * play_cols / 90 )
		place_randomly(blocks, block_cnt)
				
#}



def place_boxes():
	
	global play_rows, play_cols, classic_board, BOX

	if (classic_board):
		box_cnt = randint(210,225)
	else:
		prerange = int(play_rows * play_cols / 6)
		lower = prerange - (int(prerange * .05))
		upper = prerange + (int(prerange * .05))
		box_cnt = randint(lower,upper)
	place_randomly(BOX, box_cnt)
			


##########################################################################################################
##############################################################################-- play audio function --###
##########################################################################################################
audio = ''

def play_audio(filename):

	global audio

	system('play -q audio/' + filename + '.ogg &')
	audio = ''
	
##########################################################################################################
###############################################################################-- place the pieces -- ####
##########################################################################################################


def place_beasts(count):

	global beasts, board

	step = 0 
	while(step < count):
		row = randint(1, (board_rows - 1))
		col = randint(1, (board_cols - 1))
		if(board[row][col] == BAKGRD):
			board[row][col] = beasts[0]['chr'] 
			beasts.append({'ro':row, 'co':col, 'stg':0 })
			step += 1
			beasts[step]['stg'] = randint(1, (beasts[0]['frames']))



###########################################################################################

def hatch_monster(row, col):

	global monsters, board

	stagger = randint(1, (monsters[0]['frames']))	
	board[row][col] = MONSTER
	monsters.append({'ro':row, 'co':col,'stg':stagger })



def place_monsters(count):

	global monsters, board

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

	global monsters, beasts, eggs, board

	wait_frames = (len(beasts) + len(monsters)) * eggs[0]['incu_frames'] * (randint(1, 6)) # seconds of wait time before egg starts counting down 
	stag = randint(1, eggs[0]['frames']) # the frame that the egg counts down on
	board[row][col] = EGG(32)
	eggs.append({'ro': row, 'co': col, 'wait': wait_frames, 'stg': stag, 'sub':32})


##############################################################################################


def place_eggs(count):

	global board

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
	global eggs, board, egg_speed, lcd_time, audio


	if eggs[0]['frame'] == eggs[0]['frames']:
		eggs[0]['frame'] = 0
	else:
		eggs[0]['frame'] += 1
	if eggs[0]['incu_frame'] == eggs[0]['incu_frames']:
		eggs[0]['incu_frame'] = 0
	else:
		eggs[0]['incu_frame'] += 1


	# egg_speed, incu_frames, incu_frame, frames, frame, wait, stg
	# each egg: wait, stg
	for i in range(1, (len(eggs))):
		if (eggs[i]['wait'] > 0):
			eggs[i]['wait'] -= 1
		elif (eggs[i]['wait'] == 0) & (eggs[i]['sub'] == 32):
			eggs[i]['sub'] = 8329
		elif (eggs[i]['wait'] == 0) :
			if ((eggs[i]['stg'] == eggs[0]['frame']) & (eggs[i]['sub'] > 8320)):
				eggs[i]['sub'] -= 1
				board[eggs[i]['ro']][eggs[i]['co']] = EGG(eggs[i]['sub'])
			elif ((eggs[i]['sub'] == 8320) & (eggs[i]['stg'] == eggs[0]['frame'])):
				hatch_monster(eggs[i]['ro'], eggs[i]['co'])
				del eggs[i]
				audio = 'hatch'


##############################################################################
###############################################-- move pieces --##############
##############################################################################
def place_player():
	
	step = 0 
	while(step < 1):
		row = randint(1, (board_rows - 1))
		col = randint(1, (board_cols - 1))
		if(board[row][col] == BAKGRD):
			board[row][col] = player[0]['chr']
			step += 1
			player.append({'ro': row, 'co': col, 'tug': False })
			step += 1


def kill_player():

	global BAKGRD, player, lives, board, audio

	board[ player[1]['ro'] ][ player[1]['co'] ] = BAKGRD
	lives -= 1
	del player[1]
	place_player()

	audio = 'death'



def move_enemies(pawns): #{

	global board, player, MVU, MVL, MVD, MVR, MVUL, MVUR, MVDL, MVDR, MOVES


	if pawns[0]['frame'] == pawns[0]['frames']:
		pawns[0]['frame'] = 0
	else:
		pawns[0]['frame'] += 1



	move_priority = []
	move = ''

	breakloop = False
	lay = False
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
				move_priority = [ MVUL, MVU, MVL, MVDL, MVUR, MVD, MVR, MVDR ] # UPPER LEFT range priorities
			elif ((rdistance < 0.0) & (cdistance > 0.0) & (distance_ratio <= -.5) & (distance_ratio >= -2.0)):
				move_priority = [ MVUR, MVU, MVR, MVUL, MVDR, MVL, MVDL, MVD ] # UPPER RIGHT range priorities
			elif ((rdistance > 0.0) & (cdistance > 0.0) & (distance_ratio >= .5) & (distance_ratio <= 2.0)):
				move_priority = [ MVDR, MVD, MVR, MVDL, MVUR, MVU, MVL, MVUL ] # DOWN RIGHT range priorities
			elif ((rdistance > 0.0) & (cdistance < 0.0) & (distance_ratio <= -.5) & (distance_ratio >= -2.0)):
				move_priority = [ MVDL, MVD, MVL, MVUL, MVDR, MVU, MVR, MVUR ] # DOWN LEFT range priorities
			elif ((rdistance < 0.0) & ((abs(distance_ratio) > 2.0) | (distance_ratio == 0.0))):
				move_priority = [ MVU, MVUL, MVUR, MVL, MVR, MVDL, MVDR, MVD ] # UPWARD range priorities
			elif ((cdistance > 0.0) & ((abs(distance_ratio) < .5) | (distance_ratio == 0.0))):
				move_priority = [ MVR, MVUR, MVDR, MVU, MVD, MVUL, MVDL, MVL ] # RIGHT range priorities
			elif ((rdistance > 0.0) & ((abs(distance_ratio) > 2.0) | (distance_ratio == 0.0))):
				move_priority = [ MVD, MVDL, MVDR, MVL, MVR, MVUL, MVUR, MVU ] # DOWNWARD range priorities
			elif ((cdistance < 0.0) & ((abs(distance_ratio) < .5) | (distance_ratio == 0.0))):
				move_priority = [ MVL, MVUL, MVDL, MVU, MVD, MVUR, MVDR, MVR ] # LEFT range priorities

			priority_odds = [	#145 total
				[98, False],	#98		**********************************************
				[18, False],	#18 or 36	* These values determine the odds of moves   *
				[18, False],	#18 or 36	* for an enemy if those moves are available. *
				[4, False],	#4 or 8		* If a move has an equivalent priority to    *
				[4, False],	#4 or 8		* another, but it is a box, then its odds    *
				[1, False],	#1 or 2		* are absorbed by the other.		     *
				[1, False],	#1 or 2		* DO NOT CHANGE NUMBER OF PRIORITIES!!!!!!!  *	
				[1, False]	#1		**********************************************
			]

			for priopti in range(8): 
				# if the first priority move is the player, then take that move
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
				# if the pawn is a monster, and there is a monster or beast in the space, then lay an egg
				if ((pawns[0]['chr'] == MONSTER) & ((board[ ((pawns[pwni]['ro']) + (MOVES[move_priority[0]]['ra'])) ][ ((pawns[pwni]['co']) + (MOVES[move_priority[0]]['ca'])) ] == MONSTER) | (board[ ((pawns[pwni]['ro']) + (MOVES[move_priority[0]]['ra'])) ][ ((pawns[pwni]['co']) + (MOVES[move_priority[0]]['ca'])) ] == BEAST))):
					lay = True

			if (breakloop):
				break
	
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

def push_tree(direction):

	global player, eggs, board, MOVES, BAKGRD, BOX, MVU, MVL, MVR, MVL

	push_eggs = []  # use re.match(REGGX, char)
 
	stnce_r = player[1]['ro']
	stnce_c = player[1]['co']
	intend_r = stnce_r + MOVES[direction]['ra']
	intend_c = stnce_c + MOVES[direction]['ca']
	def probe_r(p_ind):
		return player[1]['ro'] + p_ind * MOVES[direction]['ra']
	def probe_c(p_ind):
		return player[1]['co'] + p_ind * MOVES[direction]['ca']
	def kill_r(p_ind):
		return player[1]['ro'] + (p_ind + 1) * MOVES[direction]['ra']
	def kill_c(p_ind):
		return player[1]['co'] + (p_ind + 1) * MOVES[direction]['ca']
	def ram_r(p_ind):
		return player[1]['ro'] + (p_ind - 1) * MOVES[direction]['ra']
	def ram_c(p_ind):
		return player[1]['co'] + (p_ind - 1) * MOVES[direction]['ca']



	def move_eggs():
	
		for i in range(len(push_eggs)):
			eggs[push_eggs[i]]['ro'] += MOVES[direction]['ra']
			eggs[push_eggs[i]]['co'] += MOVES[direction]['ca']
			board[ eggs[push_eggs[i]]['ro'] ][ eggs[push_eggs[i]]['co'] ] = EGG(eggs[push_eggs[i]]['sub'])

	


	def push_move():

		board[probe_r(probe)][probe_c(probe)] = board[probe_r(probe - 1)][probe_c(probe - 1)]	# make board space same as preceeding space
		player[1]['ro'] = intend_r	
		player[1]['co'] = intend_c								# make player fol and fow the player
		board[intend_r][intend_c] = player[0]['chr']						# move_player()
		move_eggs(push_eggs, direction)								# increment all push_eggs


	def kill_enemy(pawns, row, col):

		global points, audio

		for i in range(1, len(pawns)):
			if ((pawns[i]['ro'] == row) & (pawns[i]['co'] == col)):
				del pawns[i]
				board[row][col] = BAKGRD
				points += pawns[0]['pnts']



	probe = 2
	loop = True
	while (loop):

		space = board[probe_r(probe)][probe_c(probe)]
		ram_space = board[ram_r(probe)][ram_c(probe)]
		space_after = board[kill_r(probe)][kill_c(probe)]
	
		if (space == BOX):		# if space is a box
			probe += 1 		# start loop over
		elif (re.match(REGGX, space)): 	# if space is a egg
			if (space_after == BORDER) | (space_after == KILLBLOCK):	# if next block after egg is a border
				kill_enemy(eggs, probe_r, probe_c) 			# del egg from global egg list
				push_move()						# make space same as preceeding space
			else:
				for i in range(1, len(eggs)): 				# add egg to push_eggs list
					if ((eggs[i]['ro'] == probe_r(probe)) & (eggs[i]['co'] == probe_c(probe))):
						push_eggs.append(i)
				probe += 1
		elif (space == BAKGRD): 		# if space is 
			push_move()
			loop = False
		elif (space == BORDER):				# if space is a border
			if (re.match(REGGX, (board[ram_r(probe)][ram_c(probe)]))):
				kill_enemy(eggs, ram_r(probe), ram_c(probe))
			loop = False
		elif (space == KILLBLOCK):	 		# if space is a killblock
			if (re.match(REGGX, (board[ram_r(probe)][ram_c(probe)]))):
				kill_enemy(eggs, ram_r(probe), ram_c(probe))
			loop = False
		elif (space == BEAST): # if space is a beast
			if ((space_after == KILLBLOCK) | (space_after == BORDER) | (space_after == BORDER)):
				kill_enemy(beasts, probe_r(probe), probe_c(probe))
				push_move()
			loop = False
		elif (space == MONSTER):# if space is a monster	
			if ((space_after == KILLBLOCK) | (space_after == BORDER)):
				kill_enemy(monsters, probe_r(probe), probe_c(probe))
				push_move()		
			loop = False






def move_player(direction):
	global player, board, MOVES, BAKGRD, BOX, MVU, MVL, MVR, MVD

	pawns = player	
	index = 1
	char = player[0]['chr']
	row = player[1]['ro']
	col = player[1]['co']
	fow = row + MOVES[direction]['ra'] 
	fol = col + MOVES[direction]['ca']
	rtug = row - MOVES[direction]['ra']
	ctug = col - MOVES[direction]['ca']
	board[fow][fol] = char 
	if (pawns[index]['tug']) & (board[rtug][ctug] == BOX):
		board[rtug][ctug] = BAKGRD
		board[row][col] = BOX
	else:
		board[row][col] = BAKGRD
	player[index]['ro'] = fow
	player[index]['co'] = fol



def direct_move(direction):

	global player, MOVES, board

	space = board[player[1]['ro'] +  MOVES[direction]['ra'] ][ player[1]['co'] + MOVES[direction]['ca'] ]

	if (space == BAKGRD):
		move_player(direction)
#	elif (space == BOX):
#		push_tree(direction)
	elif (space == MONSTER) | (space == BEAST) | (space == KILLBLOCK):
		kill_player()



def direct_keypress(tap):	

	global player, MOVES, board

	if (tap == curses.KEY_UP):
		direct_move('U')
	elif (tap == curses.KEY_LEFT):
		direct_move('L')
	elif (tap == curses.KEY_DOWN):
		direct_move('D')
	elif (tap == curses.KEY_RIGHT):
		direct_move('R')




######################################################################
########################-- question user about board-size --##########
######################################################################



def intro():
	global ttyRows, ttyCols, screen_cols
	introhalf = 13
	introleft = int((ttyCols/2) - introhalf)
	introright = int((ttyCols/2) + introhalf)
	introquestion = ''
	
	while(introquestion != 't') & (introquestion != 'c'):
		system('clear')
		print('\n'*(int(ttyRows/2) - 10))
		print('\r' + ' '*introleft + '\u250C' + '\u2500'*(introright - introleft - 1) + '\u2510')
		print('\r' + ' '*introright + '\u2502'+ '\r' + ' '*introleft + '\u2502' + 'tty rows:' + ' '*11 + str(ttyRows))
		print('\r'+ ' '*introright + '\u2502' + '\r' + ' '*introleft + '\u2502' + 'tty columns:' + ' '*8 + str(ttyCols))
		print('\r'+ ' '*introright + '\u2502' + '\r' + ' '*introleft + '\u2502' + 'game columns:' + ' '*7 + str(screen_cols))
		print('\r'+ ' '*introleft + '\u2514' + '\u2500'*(introright - introleft - 1) + '\u2518')
		print('\n'*4)
	
		introquestion = input(
			' '*(introleft - 7)
			+ 'Enter \'t\' to play a terminal-size board.\n\n\r' 
			+ ' '*(introleft - 7)
			+ 'Enter \'c\' to play a classic sized board. . . '
			+ '\n\n\r' 
			+ ' '*int(ttyCols/2)
			)
		if (introquestion == 't'):
			classic = False
			system('clear')
		elif (introquestion == 'c'):
			classic = True 
			system('clear')
		elif (introquestion == 'q'):
			system('clear')
			exit()

	return classic



def pause():

	global ttyRows, ttyCols, screen_cols 

	pauseleft = (int(ttyCols/2) - 8)
	pausetop = (int(ttyRows/2) - 4) - (int(board_rows / 4))
	print('\033[0m')	

	print('\033[' + str(pausetop) + ';' + str(pauseleft) + 'H' + ' '*16)
	print('\033[' + str(pausetop + 1) + ';' + str(pauseleft) + 'H' + ' ' + chr(9556) + chr(9552)*12 + chr(9559) + ' ')
	print('\033[' + str(pausetop + 2) + ';' + str(pauseleft) + 'H' + ' ' + chr(9553) + '            ' + chr(9553) + ' ')
	print('\033[' + str(pausetop + 3) + ';' + str(pauseleft) + 'H' + ' ' + chr(9553) + '   PAUSED   ' + chr(9553) + ' ')
	print('\033[' + str(pausetop + 4) + ';' + str(pauseleft) + 'H' + ' ' + chr(9553) + '            ' + chr(9553) + ' ')
	print('\033[' + str(pausetop + 5) + ';' + str(pauseleft) + 'H' + ' ' + chr(9562) + chr(9552)*12 + chr(9565) + ' ')
	print('\033[' + str(pausetop + 6) + ';' + str(pauseleft) + 'H' + ' '*16)
	
	print('\033[H\033[8m')


#####################################################################################################
#######################################################-- main function calls -######################
#####################################################################################################

classic_board = intro()
system('reset')

plan_the_board()
build_the_board()

place_blocks(BLOCK)
place_boxes()

place_beasts(2)
place_monsters(2)
place_eggs(2)

place_player()

#############################################################################
##################################################-- take input func -- #####
#############################################################################
	


def take_input():
	global debug, keypress, player, top_margin, left_margin, save_top, save_left
	
	stdscr = curses.initscr() 
	curses.cbreak()
	stdscr.keypad(1)
	stdscr.refresh()

	while(True):
		keypress = stdscr.getch()
		if keypress == ord('q'):
			system('clear')
			exit()
		elif keypress == ord('p'):
			keypress = stdscr.getch()
			keypress = ''
		elif keypress == ord('r'):
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
		elif keypress == ord(' '):
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


#########################################################################################################
threading.Thread(target=take_input).start()  ###############-- the main game clock and print loop --#####
#########################################################################################################


while(True):
	if audio == 'death':
		play_audio(audio)
	elif audio == 'hatch':
		play_audio(audio)
	if keypress == ord('q'):
		system('reset')
		exit()
	elif keypress == ord('p'):
		play_audio('pause')
		pause()
		while(keypress == ord('p')):
			sleep(.05)
		game_pause = 0
		play_audio('pause')
	else:
		move_enemies(beasts)
		move_enemies(monsters)
		hatch_eggs()
		print_board(board, True)
	sleep(lcd_time)
################################################
input()
