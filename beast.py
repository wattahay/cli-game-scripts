import curses
from random import randint
from os import system, popen
from time import sleep
import threading


##################################-- starting game statistics

lives = 5		# starting lives

###############################

beast_speed = 1.5	# seconds between enemy moves
monster_speed = 1.1	# seconds between enemy moves
egg_speed = 3		# seconds between countdown

##################################-- game scoring balance

beast_scr = 2		# points for killing beasts
egg_scr = 4		# points for killing eggs
monster_scr = 6		# points for killing monsters

##################################-- game speed

lcd_time = .04

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

MVU  = 	'U'
MVD  = 	'D'
MVL  = 	'L'
MVR  = 	'R'
MVUL = 	'UL'
MVUR = 	'UR'
MVDL = 	'DL'
MVDR = 	'DR'

DIR_LIS = (MVU, MVD, MVL, MVR, MVUL, MVUR, MVDL, MVDR)

KEY_UP = 259
KEY_DOWN = 258
KEY_RIGHT = 261
KEY_LEFT = 260

keypress = '' 
debug = False
last_frame = 1
timeout = 0
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
##################################-- Pawn Lists 

# pawn lists dynamically grows and shrink with 

beasts = [{
	'frames': ((int(beast_speed / lcd_time)) - 1),
	'frame':0,
	'chr': BEAST,
	'pnts': beast_scr 
	}]

monsters = [{
	'frames': ((int(monster_speed / lcd_time)) - 1),
	'frame':0,
	'chr': MONSTER,
	'pnts': monster_scr
	}]

eggs = [{
	'frames': ((int(egg_speed / lcd_time)) - 1),
	'frame':0,
	'incu_frames': (int(1 / lcd_time)), # incu_frames add up to 1 second
	'incu_frame': 0,
	'pnts': egg_scr
	}]

# 'sub'		updated digital unicode reference to subscript character
# 'wait'	randomized wait time before hatching countdown
player = [{
		'flash_frames': (int(.05 / lcd_time) * 2),
		'chr': PLAYER,
		'pnts': 10 
	}]

plr_flashes = 5
plr_flash = 0
plr_frames = (int(.05 / lcd_time) * 2)
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

block_cnt = 10  # number of yellow blocks

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

	global stat_space, save_left, save_top
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


def print_board(board_array): #{

	global ttyCols, top_margin, left_margin, points, score, lives, level, board_rows, board_cols, save_top, save_left, stat_space, stat_rows

	print('\033[?25l\033[0m\033[' + str(top_margin)  + ';' + str(left_margin) + 'H\033[s')
						
	for rowi in range(board_rows + 1):	
		print('\033[u' + '\033[' + str(rowi) +  'B' + ''.join(board_array[rowi - 1]))		

	if (debug):
		print('\033[u' + '\033[' + str(len(board) + 4) + 'B' + '\rPlayer: ' + str(player) )
		for i in range(0, len(eggs)):
			if i == 0: print('\033[u' + '\033[' + str(len(board) + 6 + i) + 'B' + '\r\033[K\033[1B\033[K\033[1AEggs: ' + str(eggs[i]))
			else: print('\033[u' + '\033[' + str(len(board) + 6 + i) + 'B' + '\r\033[K\033[1B\033[K\033[1A\tEgg ' + str(i) + ': ' + str(eggs[i]))
		for i in range(0, len(beasts)):
			if i == 0: print('\033[u' + '\033[' + str(len(board) + len(eggs) + 7 + i) + 'B' + '\r\033[K\033[1B\033[K\033[1ABeasts: ' + str(beasts[i]))
			else: print('\033[u' + '\033[' + str(len(board) + len(eggs) + 7 + i) + 'B' + '\r\033[K\033[1B\033[K\033[1A\tBeast ' + str(i) + ': ' + str(beasts[i]))
		for i in range(0, len(monsters)):
			if i == 0: print('\033[u' + '\033[' + str(len(board) + len(eggs) + len(beasts) + 8 + i) + 'B' + '\r\033[K\033[1B\033[K\033[1AMonsters: ' + str(monsters[i]))
			else: print('\033[u' + '\033[' + str(len(board) + len(eggs) + len(beasts) + 8 + i) + 'B' + '\r\033[K\033[1B\033[K\033[1A\tMonster ' + str(i) + ': ' + str(monsters[i]))
		 
	print('\033[u' + '\033[' + str(len(board) + 2) + 'B' + '\033[' + str(stat_space) + 'C' + '\033[s' + chr(9477) + 
	' ' + 'TOTAL: ' + str(score)  + 	' ' + chr(9477) + '\033[u\033[' + str((stat_space + 14) * 1) + 'C' + chr(9477) + 
	' ' + 'TALLY: ' + str(points) + 	' ' + chr(9477) + '\033[u\033[' + str((stat_space + 14) * 2) + 'C' + chr(9477) + 
	' ' + 'LIVES: ' + str(lives)  +  	' ' + chr(9477) + '\033[u\033[' + str((stat_space + 14) * 3) + 'C' + chr(9477) + 
	' ' + 'LEVEL: ' + str(level)  +  	' ' + chr(9477)) 

	print('\033[H\033[8m')

##########################################################################################################
##############################################################################-- play audio function --###
##########################################################################################################

def play_audio(filename): system('aplay -q audio/' + filename + '.wav &')

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

	wait_frames = (len(eggs) + len(beasts) + len(monsters)) * eggs[0]['incu_frames'] + (randint(1, 30)) # seconds of wait time before egg starts counting down 
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
	
	di = 0 # keeps track of index to accomodate for egg deletions

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


def push_tree(intent):

	global player, eggs, board, BLOCK, MOVES, BAKGRD, BOX, MVU, MVL, MVR, MVL, PLAYER

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
			elif ((wall_space == BAKGRD) | (wall_space == BOX)):
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
	global PLAYER, board, MOVES, BAKGRD, BOX, MVU, MVL, MVR, MVD

	index = 1
	row = player[1]['ro']
	col = player[1]['co']
	fow = row + MOVES[direction]['ra'] 
	fol = col + MOVES[direction]['ca']
	rtug = row - MOVES[direction]['ra']
	ctug = col - MOVES[direction]['ca']
	board[fow][fol] = PLAYER 
	if (player[index]['tug']) & (board[rtug][ctug] == BOX):
		board[rtug][ctug] = BAKGRD
		board[row][col] = BOX
	else:
		board[row][col] = BAKGRD
	player[index]['ro'] = fow
	player[index]['co'] = fol



def direct_move(tap_move):

	global player, MOVES, board

	space = board[player[1]['ro'] +  MOVES[tap_move]['ra'] ][ player[1]['co'] + MOVES[tap_move]['ca'] ]

	if (space == BAKGRD):
		move_player(tap_move)
	elif (space == BOX):
		push_tree(tap_move)
	elif (space == MONSTER) | (space == BEAST) | (space == KILLBLOCK):
		kill_player()



def direct_keypress(tap):

	global player, MOVES, board, KEY_UP, KEY_DOWN, KEY_RIGHT, KEY_LEFT

	if (tap == KEY_UP):
		direct_move('U')
	elif (tap == KEY_LEFT):
		direct_move('L')
	elif (tap == KEY_DOWN):
		direct_move('D')
	elif (tap == KEY_RIGHT):
		direct_move('R')




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
	
	global game_play_mode, keypress, stdscr, play_rows, play_cols, board_rows, board_cols, reset_board, blank_board, board, beast_cnt, monster_cnt, egg_cnt, level, lives, score, points, BAKGRD, BLOCK, KILLBLOCK, last_frame, top_margin, left_margin, lcd_time, KEY_UP, KEY_DOWN, KEY_RIGHT, KEY_LEFT

	game_play_mode = False # sets the input loop to reject player move functions and other functions reserved for game play time	

	stdscr = curses.initscr() 
	stdscr.keypad(1)
	stdscr.refresh()

	block_type = BLOCK
	lvl_beast_cnt = 0
	lvl_monster_cnt = 0
	lvl_egg_cnt = 0
	lvl_box_cnt = 0
	lvl_block_cnt = block_cnt
	
	print_board(board)
	sleep(.5)
	board = []
	board = build_the_board()
	print_board(board)

	print('\033[' + str(top_margin + 5) + ';' + str(left_margin + (board_cols - 30)) + 'H\033[s\033[0m')

	if (level == 0):
		sleep(.6)
		print('\033[u\033[2B' + BEAST*4 + BAKGRD*2 + BEAST*5 + BAKGRD*3 + BEAST*1 + BAKGRD*4 + BEAST*3 + BAKGRD*2 + BEAST*5
			+ '\033[u\033[3B' + BEAST*1 + BAKGRD*3 + BEAST*1 + BAKGRD*1 + BEAST*1 + BAKGRD*6 + BEAST*1 + BAKGRD*1 + BEAST*1 + BAKGRD*2 + BEAST*1 + BAKGRD*3 + BEAST*1 + BAKGRD*3 + BEAST*1
			+ '\033[u\033[4B' + BEAST*1 + BAKGRD*3 + BEAST*1 + BAKGRD*1 + BEAST*1 + BAKGRD*5 + BEAST*1 + BAKGRD*3 + BEAST*1 + BAKGRD*1 + BEAST*1 + BAKGRD*7 + BEAST*1
			+ '\033[u\033[5B' + BEAST*4 + BAKGRD*2 + BEAST*3 + BAKGRD*3 + BEAST*5 + BAKGRD*2 + BEAST*3 + BAKGRD*4 + BEAST*1
			+ '\033[u\033[6B' + BEAST*1 + BAKGRD*3 + BEAST*1 + BAKGRD*1 + BEAST*1 + BAKGRD*5 + BEAST*1 + BAKGRD*3 + BEAST*1 + BAKGRD*5 + BEAST*1 + BAKGRD*3 + BEAST*1
			+ '\033[u\033[7B' + BEAST*1 + BAKGRD*3 + BEAST*1 + BAKGRD*1 + BEAST*1 + BAKGRD*5 + BEAST*1 + BAKGRD*3 + BEAST*1 + BAKGRD*1 + BEAST*1 + BAKGRD*3 + BEAST*1 + BAKGRD*3 + BEAST*1
			+ '\033[u\033[8B' + BEAST*4 + BAKGRD*2 + BEAST*5 + BAKGRD*1 + BEAST*1 + BAKGRD*3 + BEAST*1 + BAKGRD*2 + BEAST*3 + BAKGRD*4 + BEAST*1)
		print('\033[u\r\033[' + str(left_margin + 3) + 'C\033[3A\033[40m\033[2mPress the Spacebar to Play . . .\033[1B\033[0m')
		while (keypress != ord(' ')):
			sleep(.2)

	print('\033[u\r\033[' + str(left_margin + 3) + 'C\033[3A\033[40m\033[2mPress \'tab\' for Options Menus . . .\033[1B\033[0m\033[8m')
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

	if level == 1:
		lvl_beast_cnt = 3
		lvl_monster_cnt = 0
		lvl_egg_cnt = 0
		block_type = BLOCK
	elif level == 2:
		lvl_beast_cnt = 5
		lvl_monster_cnt = 0
		lvl_egg_cnt = 0
		block_type = KILLBLOCK
	elif level == 3:
		lvl_beast_cnt = 5
		lvl_monster_cnt = 0
		lvl_egg_cnt = 2
		block_type = BLOCK
	elif level == 4:
		lvl_beast_cnt = 4
		lvl_monster_cnt = 1 
		lvl_egg_cnt = 1
		block_type = KILLBLOCK
	elif level == 5:
		lvl_beast_cnt = 4
		lvl_monster_cnt = 2
		lvl_egg_cnt = 2
		block_type = BLOCK
	elif level == 6:
		lvl_beast_cnt = 8
		lvl_monster_cnt = 0 
		lvl_egg_cnt = 0
		block_type = KILLBLOCK
	elif level == 7:
		lvl_beast_cnt = 0
		lvl_monster_cnt = 0 
		lvl_egg_cnt = 8
		block_type = KILLBLOCK
	elif level == 8:
		lvl_beast_cnt = 0
		lvl_monster_cnt = 8 
		lvl_egg_cnt = 0
		block_type = KILLBLOCK
	elif level == 9:
		lvl_beast_cnt = 3
		lvl_monster_cnt = 3
		lvl_egg_cnt = 3
		block_type = BLOCK
	elif level == 10:
		lvl_beast_cnt = 2
		lvl_monster_cnt = 4
		lvl_egg_cnt = 3
		block_type = BLOCK
	elif level == 11:
		lvl_beast_cnt = 1
		lvl_monster_cnt = 5
		lvl_egg_cnt = 4
		block_type = KILLBLOCK
	elif level == 12:
		lvl_beast_cnt = 1
		lvl_monster_cnt = 6
		lvl_egg_cnt = 4
		block_type = KILLBLOCK
	elif level == 13:
		lvl_beast_cnt = 0
		lvl_monster_cnt = 0
		lvl_egg_cnt = 12
		block_type = KILLBLOCK
	elif level == 14:
		lvl_beast_cnt = 0
		lvl_monster_cnt = 12
		lvl_egg_cnt = 0
		block_type = KILLBLOCK
	elif level == 15:
		lvl_beast_cnt = 15
		lvl_monster_cnt = 0
		lvl_egg_cnt = 0
		block_type = KILLBLOCK
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

	main_menu = 0
	item_menu = 0
	controls_menu = 9
	menu_ref = '\033[' + str(top_margin + 3) + ';' + str(left_margin + 6) + 'H\033[s\033[0m'
	ltab = '\033[7m\033[40m'
	dtab = '\033[7m\033[40m\033[2m'
	dspeedbg = ' \033[7m\033[2;34m   \033[2;32m     \033[2;33m\033[2;31m  \033[0m\033[2m\033[40m '
	lspeedbg = ' \033[44m   \033[42m     \033[43m\033[41m  \033[0m\033[2m\033[40m '
	speedbg = dspeedbg
	speedarrow = chr(10219)
	norm = '\033[0m\033[40m'
	dnorm = '\033[0m\033[40m\033[2m'
	darkhl = '\033[2m'
	lighthl = '\033[1m'
	highlight = darkhl 
	chr_cnt = 0
	key_tracker = 0

	def main_menu_1():
		print('\033[u\033[3B' + dnorm + 'Movement Keys:  w,a,s,d   arrows   vi (h,j,k,l) ')
		print('\033[u\033[5B' + dnorm + 'Pulling Boxes:  toggle   single   switch')


	def main_menu_2():
		print('\033[u\033[4B\033[34C' + dnorm + 'Total Spaces: \033[36m' + str(play_rows * play_cols) + norm)
		print('\033[u\033[5B\033[35C' + dnorm + 'Used Spaces: \033[36m' 
			+ str(lvl_block_cnt + lvl_box_cnt + lvl_monster_cnt + lvl_beast_cnt + lvl_egg_cnt) + norm)
		print('\033[u\033[6B\033[35C' + dnorm + 'Free Spaces: \033[36m' 
			+ str((play_rows * play_cols) - (lvl_block_cnt + lvl_box_cnt + lvl_monster_cnt + lvl_beast_cnt + lvl_egg_cnt)) + norm)

		print('\033[u\033[3B' + dnorm + BEAST + '\033[40m\033[2m - Beast Count: \033[35m' + str(lvl_beast_cnt) + norm)
		print('\033[u\033[5B' + dnorm + MONSTER + '\033[40m\033[2m - Monster Count: \033[35m' + str(lvl_monster_cnt) + norm)
		print('\033[u\033[7B' + dnorm + EGG(32) + '\033[40m\033[2m - Egg Count: \033[35m' + str(lvl_egg_cnt) + norm)
		print('\033[u\033[9B' + dnorm + BOX + '\033[40m\033[2m - Box Count: \033[35m' + str(lvl_box_cnt) + norm)
		print('\033[u\033[11B' + dnorm + block_type + '\033[40m\033[2m - Block Count: \033[35m' + str(lvl_block_cnt) + norm)
		print('\033[u\033[13B' + dnorm + block_type + '\033[40m\033[2m - Block Type: Normal Yellow   Dangerous Orange ' + norm)

	def main_menu_3():
		print('\033[u\033[3B' + dnorm + BEAST + dnorm + ' - Beast:\t\t slower' + speedbg + 'faster')
		print('\033[u\033[5B' + dnorm + MONSTER + dnorm + ' - Monster:\t\t slower' + speedbg + 'faster')
		print('\033[u\033[7B' + dnorm + EGG(32) + dnorm + ' - Egg Incubate:\t slower' + speedbg + 'faster')
		print('\033[u\033[9B' + dnorm + EGG(8320) + dnorm + ' - Egg Timer:\t slower' + speedbg + 'faster')

	if keypress == 9:
		sleep(1.5)
		keypress == 999
		print_board(blank_board)
		print(menu_ref)
		while (True):
			if keypress == 9:
				keypress = ''
				main_menu += 1
				play_audio('menu_tab')
				if main_menu > 3:
					main_menu = 1
				if main_menu == 1:
					print_board(blank_board) 
					print(menu_ref)
					print('\033[u' + chr(9473) + dtab + ' key options ' + norm + chr(9473) + dtab + ' level setup ' + norm + chr(9473) + dtab + ' pawn speeds ' + norm + chr(9473)*20)
					sleep(.08)
					print('\033[u' + chr(9473) + ltab + ' key options ' + norm + chr(9473) + dtab + ' level setup ' + norm + chr(9473) + dtab + ' pawn speeds ' + norm + chr(9473)*20)
					main_menu_1()
				elif main_menu == 2:
					print_board(blank_board) 
					print(menu_ref)
					print('\033[u' + chr(9473) + dtab + ' key options ' + norm + chr(9473) + dtab + ' level setup ' + norm + chr(9473) + dtab + ' pawn speeds ' + norm + chr(9473)*20)
					sleep(.08)
					print('\033[u' + chr(9473) + dtab + ' key options ' + norm + chr(9473) + ltab + ' level setup ' + norm + chr(9473) + dtab + ' pawn speeds ' + norm + chr(9473)*20)
					main_menu_2()
				elif main_menu == 3:
					print_board(blank_board) 
					print(menu_ref)
					print('\033[u' + chr(9473) + dtab + ' key options ' + norm + chr(9473) + dtab + ' level setup ' + norm + chr(9473) + dtab + ' pawn speeds ' + norm + chr(9473)*20)
					sleep(.08)
					print('\033[u' + chr(9473) + dtab + ' key options ' + norm + chr(9473) + dtab + ' level setup ' + norm + chr(9473) + ltab + ' pawn speeds ' + norm + chr(9473)*20)
					main_menu_3()


			elif ((keypress == KEY_UP) | (keypress == KEY_DOWN)):		

				if (main_menu == 1):
				
					main_menu_1()	
					if (keypress == KEY_UP):
						item_menu -= 1
						if item_menu < 0: item_menu = 2
					elif (keypress == KEY_DOWN): 
						item_menu += 1
						if item_menu > 2: item_menu = 0
					if (item_menu != 0): 
						play_audio('menu_item')
					if (item_menu == 1): 
						print('\033[u\033[0m\033[40m\033[3BMovement Keys:  w,a,s,d   arrows   vi (h,j,k,l) ')
						keypress = 999
					elif (item_menu == 2):
						print('\033[u\033[0m\033[40m\033[5BPulling Boxes:  toggle   single   switch')
						keypress = 999
					while (keypress == 999):
						sleep(lcd_time)

				elif (main_menu == 2):
					main_menu_2()
					if (keypress == KEY_UP):
						item_menu -= 1
						if item_menu < 2: 
							item_menu = 8
					elif (keypress == KEY_DOWN): 
						item_menu += 1
						if item_menu > 8: 
							item_menu = 2
					if (item_menu != 2): 
						play_audio('menu_item')
					if (item_menu == 3): 
						print('\033[u\033[3B\033[40m' + BEAST + '\033[40m - Beast Count: \033[35m' + str(lvl_beast_cnt) + norm)
						keypress = 999
					elif (item_menu == 4):
						print('\033[u\033[5B\033[40m' + MONSTER + '\033[40m - Monster Count: \033[35m' + str(lvl_monster_cnt) + norm)
						keypress = 999
					elif (item_menu == 5):
						print('\033[u\033[7B\033[40m' + EGG(32) + '\033[40m - Egg Count: \033[35m' + str(lvl_egg_cnt) + norm)
						keypress = 999
					elif (item_menu == 6):
						print('\033[u\033[9B\033[40m' + BOX + '\033[40m - Box Count: \033[35m' + str(lvl_box_cnt) + norm)
						keypress = 999
					elif (item_menu == 7):
						print('\033[u\033[11B\033[40m' + block_type + '\033[40m - Block Count: \033[35m' + str(lvl_block_cnt) + norm)
						keypress = 999
					elif (item_menu == 8):
						print('\033[u\033[13B\033[40m' + block_type + '\033[40m - Block Type: Normal Yellow   Dangerous Orange ' + norm)
						keypress = 999
					while (keypress == 999):
						sleep(lcd_time)

				elif (main_menu == 3):
					main_menu_3()
					if (keypress == KEY_UP):
						item_menu -= 1
						if item_menu < 8: 
							item_menu = 12
					elif (keypress == KEY_DOWN): 
						item_menu += 1
						if item_menu > 12: 
							item_menu = 8
					if (item_menu != 8): 
						play_audio('menu_item')
					if (item_menu == 9):
						print('\033[u\033[3B\033[40m' + BEAST + '\033[40m - Beast:' + '\033[2m\033[40m\t\t slower' + speedbg + 'faster')
						keypress = 999
					elif (item_menu == 10):
						print('\033[u\033[5B\033[40m' + MONSTER + '\033[40m - Monster:\t' + '\033[2m\033[40m\t slower' + speedbg + 'faster')
						keypress = 999
					elif (item_menu == 11):
						print('\033[u\033[7B\033[40m' + EGG(32) + '\033[40m - Egg Incubate:   ' + '\033[2m\033[40m\t slower' + speedbg + 'faster')
						keypress = 999
					elif (item_menu == 12):
						print('\033[u\033[9B\033[40m' + EGG(8320) + '\033[40m - Egg Timer:' + '\033[2m\033[40m\t slower' + speedbg + 'faster')
						keypress = 999
					while (keypress == 999):
						sleep(lcd_time)


			if keypress == 27:
				keypress = ''
				print_board(blank_board)
				sleep(1)
				break
			sleep(lcd_time)			

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
	game_play_mode = True

####################################################################################################
#########################################################################-- take input func -- #####
####################################################################################################

def take_input():

	global stdscr, debug, keypress, player, top_margin, left_margin, save_top, save_left, key_move, timeout, game_play_mode

	stdscr = curses.initscr() 
	stdscr.keypad(1)
	stdscr.refresh()
	
	while(True):
		sleep(lcd_time - .02)
		keypress = stdscr.getch()
		system('echo \'' + str(keypress) + '\' >> level.txt')
		timeout = 0
		if (game_play_mode):
			if keypress == 27: # the esc key
				system('clear')
				exit()
			elif keypress == ord('p'):
				keypress = stdscr.getch()
				keypress = ''
			elif keypress == ord('r'):
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
	

system('reset')
plan_the_board()
############################################################################################################
threading.Thread(target=take_input).start()  ###############-- the main game clock and print loop --#####
last_frame = 1

while(True):
	if timeout > 2:
		keypress = ord('p')
		timeout = 0
	if keypress == 27:
		system('clear')
		exit()
	elif keypress == ord('p'):
		pause()
	else:
		if ((lives == 0) | ((len(beasts) == 1) & (len(monsters) == 1) & (len(eggs) == 1))):
			if last_frame == 0:
				if lives == 0: play_audio('loss')
				elif level != 0: play_audio('win')
				build_level()								
			last_frame -= 1
		move_enemies(beasts)
		move_enemies(monsters)
		hatch_eggs()
		flash_player()
		print_board(board)
	sleep(lcd_time)

################################################
input()
