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

max_play_rows = 35 	# alter max game height here
max_play_cols = 65 	# alter max game width here
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
lcd_time = .01666111 * 4

###############################

beast_speed = 1.5	# seconds between enemy moves
monster_speed = 1.5	# seconds between enemy moves
egg_speed = 4		# seconds between countdowns

min_incubate = 5	# minimum time before eggs start counting down
max_incubate = 30	# maximum time before eggs start counting down


		# frame-rate of entire game (CODISTADIT)

####################################-- pawn move constants
# di - direction
# ra - row adjustment
# ca - column adjustment
# mm - move multiplier for converting absolute values
# tr - tug row adder if the palyer is moving that direction
# tc - tug col adder if the player is moving that direction


MOVES = {
'U': {	'di':'U', 	'ra':-1, 	'ca':0, 	'tr':1,		'tc':0,		'mm':-1},
'D': {	'di':'D', 	'ra':1, 	'ca':0, 	'tr':-1,	'tc':0,		'mm':1},
'L': {	'di':'L', 	'ra':0, 	'ca':-1, 	'tr':0,		'tc':1,		'mm':-1},
'R': {	'di':'R',	'ra':0, 	'ca':1, 	'tr':0,		'tc':-1,	'mm':1},
'UL': {	'di':'UL',	'ra':-1, 	'ca':-1},
'UR': {	'di':'UR', 	'ra':-1, 	'ca':1},
'DL': {	'di':'DL', 	'ra':1, 	'ca':-1},
'DR': {	'di':'DR', 	'ra':1, 	'ca':1}
}

RA = 'ra'
CA = 'ca'
TR = 'tr'
TC = 'tc'
MM = 'mm'
DI = 'di'

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

eggsub = 8329			# unicode key for subscript 9 (8328 = 8, and so on)
egg2nd = 32			# unicode key for a space character 
REGGX = re.compile('\u2B2C.') 	# use re.match(REGGX, char) to see if a piece is an egg

# (ANSI styles)	 FG   + 	BG   + 		Style +		Characters +			Reset
BAKGRD = 							'  ' 
BLOCK =		       		'\033[43m' +         		'  ' + 				'\033[0m'
KILLBLOCK = 			'\033[43m' +	'\033[1m' +	'  ' + 				'\033[0m'
BOX = 		'\033[32m' +					chr(9618) + chr(9618) +		'\033[0m'
EGG = 		'\033[37m' +					chr(11052) + chr(egg2nd) + 	'\033[0m'
BEAST = 	'\033[31m' +					chr(9500) + chr(9508) +		'\033[0m'
MONSTER = 	'\033[31m' +					chr(9568) + chr(9571) +		'\033[0m'
PLAYER = 	'\033[34m' +					chr(9664) + chr(9654) +		'\033[0m'
# http://wiki.bash-hackers.org/scripting/terminalcodes

###################################-- Pawn Classes (Dictionaries)
##################################-- Pawn Lists 

# pawn lists dynamically grows and shrink with 

RO = 'ro'
CO = 'co'
FOW = 'fow'
FOL = 'fol'
STG = 'stag'
MV = 'mv'
PSH = 'push'
TUG = 'tug'

beasts = [{
	'chr': BEAST, 
	'frame':0,
	'frames': ((int(beast_speed / lcd_time)) - 1)
	}]

monsters = [{
	'chr': MONSTER, 
	'frame':0,
	'frames': ((int(beast_speed / lcd_time)) - 1)
	}]

eggs = [{
	'chr': EGG, 
	'frame':0,
	'frames': ((int(beast_speed / lcd_time)) - 1)
	}]

# 'sub'		updated digital unicode reference to subscript character
# 'wait'	randomized wait time before hatching countdown
player = [{
		'chr': PLAYER, 
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

game_pause = 0

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

	global top_margin, left_margin, board_rows, board_cols, play_rows, play_cols, min_play_rows, min_play_cols, max_play_rows, max_play_cols, stat_rows, ttyCols, screen_rows, screen_cols

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


	#intro = board
	#roster = board
	#controls = board
	#info = board

	#global intro, roster, controls, info
#}






def print_board(board_array, stats): #{

	global ttyCols, top_margin, left_margin, score, lives, level, board_rows, board_cols


	# Hide the cursor
	system('tput civis')
	
	bottom_margin = top_margin - 3

	#     |
	#     V
	#     |
	#     V
	#     |
	#     V
	#     |
	#     V
	#########-- Print Top Margin	
	print('\n'*top_margin)
	
						#########################################
						#					#
	#########-- Print Left Margin ->->->->	#	H				#
	#########-- Print Board			#		H	<>		#
	for rowi in range(board_rows):		#					#
		print('\r' + ' '*left_margin + ''.join(board_array[rowi]))		#
						#				H	#
						#					#
						#	H				#
						#########################################
	#########-- Print Game Stats -------->  Score: 200  Lives: 4  Level: 3
	if (stats):
		print('\r' + ' '*left_margin + '   SCORE: ' + str(score) + '   LIVES: ' + str(lives) + '    LEVEL: ' + str(level)) 

	########-- Print Debug Stats
	if (debug):
		print(
			'\n\r Player: ' + str(player) +
			'\n\rBeasts: ' + str(beasts) +
			'\n\rBeast Stepper: ' + str(beasts[0]['frame'])
		 ) 
	#}

	



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
def place_blocks(): #{

	global play_rows, play_cols, BLOCK

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
			board[rowi][coli] = BLOCK
			step -= 1
			del col_ranges[col_range_index]
			del row_ranges[row_range_index]
	else:
		block_cnt = round(play_rows * play_cols / 90 )
		place_randomly(BLOCK, block_cnt)
				
#}

def place_boxes():
	
	global play_rows, play_cols, classic_board, BOX

	if (classic_board):
		box_cnt = randint(210,225)
	else:
		prerange = int(play_rows * play_cols / 4)
		lower = prerange + (int(prerange / 20))
		upper = prerange + (int(prerange / 20 * 2))
		box_cnt = randint(lower,upper)
	place_randomly(BOX, box_cnt)
			

	
#############################################################################
##################################################-- place the pieces -- ####
#############################################################################



def place_pawns(pieces, count):

	pawn = pieces[0]['chr']
	step = 0 
	while(step < count):
		row = randint(1, (board_rows - 1))
		col = randint(1, (board_cols - 1))
		if(board[row][col] == BAKGRD):
			board[row][col] = pawn 
			pieces.append({'ro':row, 'co':col, 'tug':False, 'stag':0})
			if (pawn != PLAYER):
				pieces[step]['stag'] = randint(1, (pieces[0]['frames']))
			step += 1

	return pieces
	

##############################################################################
##############################################-- move pieces --##############
##############################################################################
def start_level():

	global beasts, monsters, eggs, player, board

	build_the_board()
	sleep(.3)
	print_board(board, False)
	place_blocks()
	sleep(.3)
	system('clear')
	print_board(board, False)
	place_boxes()
	sleep(.3)
	system('clear')
	print_board(board, False)
	sleep(.3)
	beasts = place_pawns(beasts, beast_cnt)
	sleep(.3)
	system('clear')
	print_board(board, False)
	monsters = place_pawns(monsters, monster_cnt)
	sleep(.3)
	system('clear')
	print_board(board, False)
	eggs = place_pawns(eggs, egg_cnt)
	sleep(.3)
	system('clear')
	print_board(board, False)
	player = place_pawns(player, 1 )
	sleep(.3)
	system('clear')
	print_board(board, True)
	sleep(.3)
	




def game_intro():

	global intro, roster, controls, info




def win_level():

	global score, points, level, beasts, monsters, eggs, player, beast_cnt, monster_cnt, egg_cnt
	
	score += points
	points = 0
	level += 1





def lose_level():

	global score, points, level, beasts, monsters, eggs, player, beast_cnt, monster_cnt, egg_cnt
	
	score += points
	points = 0
	level -= 1
	if (level == 0):
		game_intro()
	else:
		start_level()




##############################################################################
##############################################-- move pieces --##############
##############################################################################


def kill_player():

	global board, player, lives, score, points

	lives -= 1
	points += death_scr
	board[player[1][RO]][player[1][CO]] = BAKGRD
	
	if (lives == 0):
		lose_level() 
	else:
		del player[1]
		place_pawns(player)





def move_enemies(pawns): #{

	global board, player, MVU, MVL, MVD, MVR, MVUL, MVUR, MVDL, MVDR

	move_priority = []
			
	for pwni in range(1, len(pawns)): 	# in a given frame, loops through all pawns in a list
						# if the pawn is staggered to move in the present frame,
						# the pawn moves to a space
		if (pawns[pwni][STG] == pawns[0]['frame']):
			rdistance = player[1][RO] - pawns[pwni][RO]
			cdistance = player[1][CO] - pawns[pwni][CO]
	
			distance_ratio = rdistance / cdistance
			if ((rdistance > 0) & (cdistance < 0) & (distance_ratio < -.5) & (distance_ratio > -2)):
				move_priority = ( MVDL, MVD, MVL, MVUL, MVDR, MVU, MVR, MVUR ) # DOWN LEFT range priorities
			elif ((rdistance > 0) & (cdistance > 0) & (distance_ratio > .5) & (distance_ratio < -2)):
				move_priority = ( MVDR, MVD, MVR, MVDL, MVUR, MVU, MVL, MVUL ) # DOWN RIGHT range priorities
			elif ((rdistance < 0) & (cdistance > 0) & (distance_ratio < -.5) & (distance_ratio > -2)):
				move_priority = ( MVUR, MVU, MVR, MVUL, MVDR, MVL, MVDL, MVD ) # UPPER RIGHT range priorities
			elif ((rdistance < 0) & (cdistance < 0) & (distance_ratio > -.5) & (distance_ratio < 2)):
				move_priority = ( MVUL, MVU, MVL, MVDL, MVUR, MVD, MVR, MVDR ) # UPPER LEFT range priorities
			elif ((rdistance < 0) & ((abs(distance_ratio) > 2) | (distance_ratio == 0))):
				move_priority = ( MVU, MVUL, MVUR, MVL, MVR, MVDL, MVDR, MVD ) # UPWARD range priorities
			elif ((rdistance > 0) & ((abs(distance_ratio) >= 2) | (distance_ratio == 0))):
				move_priority = ( MVD, MVDL, MVDR, MVL, MVR, MVUL, MVUR, MVU ) # DOWNWARD range priorities
			elif ((cdistance > 0) & ((abs(distance_ratio) <= .5) | (distance_ratio == 0))):
				move_priority = ( MVR, MVUR, MVDR, MVU, MVD, MVUL, MVDL, MVL ) # RIGHT range priorities
			elif ((cdistance < 0) & ((abs(distance_ratio) < .5) | (distance_ratio == 0))):
				move_priority = ( MVL, MVUL, MVDL, MVU, MVD, MVUR, MVDR, MVR ) # LEFT range priorities

			priority_odds(		#199
				(150, True),	#150		**********************************************
				(18, True),	#18 or 36	* These values determine the odds of moves   *
				(18, True),	#18 or 36	* for an enemy if those moves are available. *
				(4, True),	#4 or 8		* If a move has an equivalent priority to    *
				(4, True),	#4 or 8		* another, but it is a box, then its odds    *
				(1, True),	#2 or 4		* are absorbed by the other.		     *
				(1, True),	#2 or 4		* DO NOT CHANGE NUMBER OF PRIORITIES!!!!!!!  *	
				(1, True)	#1		**********************************************
			)

			likely_move = ''

			for priopti in range(len(move_priority) - 1): 
				# if the first priority move is the player, then take that move
				if (board[pawns[pwni][RO] + MOVES[move_priority[0]][ 'ra' ]][pawns[pwni][CO] + MOVES[move_priority[0]][ 'ca' ]] == PLAYER):
					pawns[plyr][MV] = move_priority[priopti]
					pawns[plyr][RO] = player[1][RO]
					pawns[plyr][CO] = player[1][CO]
					kill_player()
					board[pawns[plyr][RO]][pawns[plyr][CO]] = pawns[0]['chr']
				#elif ((player == BEAST) & (board[][] == MONSTER)) | ((player == MONSTER) & ((board[][] == MONSTER) | (board[][] == BEAST))):
					#lay_egg()
				# else if the first priority move is not available, then mark it as unavailable
				elif (board[pawns[pwni][RO] + MOVES[move_priority[0]][ 'ra' ]][pawns[pwni][CO] + MOVES[move_priority[0]][ 'ca' ]] != BAKGRD):
					priority_odds[priopti][1] = False
				
			for prioddi in range(len(priority_odds) - 1): # loop through priorities to add them to likely_moves if available
				if (priority_odds[prioddi][1])): # if it is true that the priority move is a blank space, then loop through and fill out the likely_moves list
					for i in range(priority_odds[prioddi][0]): # loop through by number in "priorities" loop, to fill out likely_moves list
						if ((prioddi % 2) == 0) & (prioddi != 0) & (not priority_odds[prioddi - 1])):
						# if the even priority is the only available move for that priority, then double the even priority
							for i in range(priority_odds[prioddi][0]):
 								likely_move.append(move_priorites(prioddi))
						if ((prioddi % 2) == 1) & (prioddi != 7) & (not priorities[prioddi + 1])):
						# if the odd priority is the only available move for that priority, then double the odd priority
							for i in range(priorities[prioddi][0]):
								likely_move.append(move_priority(prioddi))
						else:
						# otherwise, add the even or odd move the normal amount for its singular availability
							likely_move.append(move_priority(prioddi))

			# we have calculated 
			pawns[plyr][MV] = likely_move(randint(0, len(likely_move - 1))
			board[][] = pawn[0]['chr']
			board[][] = BAKGRD

#}



	

def box_push(push_eggs, explode):

	# if explode = True
		# if leading space is an egg

def push_tree():

	global MVU, MVL, MVD, MVR, MOVES 

	probe = 1
	egg = False
	loop = True
	push_eggs = []	
	probe_row = 0
	probe_col = 0
	explode = False

	while (loop):
		# if space is a bakgrd
		
			# make board space same as preceeding space
			# make player fol and fow the player
			# move_player()
			# increment all push_eggs
			# change board spaces for all push_eggs
		# if space is a box
			# start loop over
		# if space is a border
			# exit loop (loop = False)
			# clear push_eggs list
		# if space is a killblock
			# delete any leading egg from push_eggs AND eggs list
			# increment all other eggs in push_eggs
			# move_player()
			# make old player space a bakgrd
			# 
		# if space is a egg
			# if next block after egg is a border
				# del egg from global egg list
				# add egg kill points to level points
				# make space same as preceeding space
				# move_player()
				# increment all push_eggs
				# change board spaces for all push_eggs
			# else:
				# add egg to push_eggs list
			# start loop over
		# if space is a beast
			# if the next block after the beast is a box or border
				# delete beast from list
				# add beast level kill points
				# make board space same as preceeding space
				# make player fol and fow the player
				# move_player()
				# increment all push_eggs
				# change board spaces for all push_eggs
		# if space is a monster	
			# if the next block is a border
				# delete monster from list
				# add monster level kill points
				# make board space same as preceeding space
				# make board space for player fol and fow the player
				# move_player()
				# increment all push_eggs
				#  






def player_move(tap):	

	global board, player, MVU, MVL, MVD, MVR

	if (tap == curses.KEY_UP):
		player[1][MV] = MVU
	elif (tap == curses.KEY_LEFT):
		player[1][MV] = MVL
	elif (tap == curses.KEY_DOWN):
		player[1][MV] = MVD
	elif (tap == curses.KEY_RIGHT):
		player[1][MV] = MVR

	player[1][FOW] = player[1][RO] + MOVES[player[1][MV]][RA] # prospective row move for player
	player[1][FOL] = player[1][CO] + MOVES[player[1][MV]][CA] # prospective column move for player
	
	if (player[1][TUG]):
		player[1][TOW] = player[1][RO] + MOVES[player[1][MV]][TR] # prospective row move for player
		player[1][TOL] = player[1][CO] + MOVES[player[1][MV]][TC] # prospective column move for player
	

	if (board[player[1][FOW]][player[1][FOL]] == BAKGRD):
		move_player()
	elif ((board[player[1][FOW]][player[1][FOL]] == BEAST) | (board[player[1][FOW]][player[1][FOL]] == MONSTER) (board[player[1][FOW]][player[1][FOL]] == KILLBLOCK)):
		kill_player()
	elif (board[player[1][FOW]][player[1][FOL]] == BOX):
		push_tree()

		




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
	
	print('\033[' + str(pausetop) + ';' + str(pauseleft) + 'H' + ' '*16)
	print('\033[' + str(pausetop + 1) + ';' + str(pauseleft) + 'H' + ' ' + chr(9556) + chr(9552)*12 + chr(9559) + ' ')
	print('\033[' + str(pausetop + 2) + ';' + str(pauseleft) + 'H' + ' ' + chr(9553) + '            ' + chr(9553) + ' ')
	print('\033[' + str(pausetop + 3) + ';' + str(pauseleft) + 'H' + ' ' + chr(9553) + '   PAUSED   ' + chr(9553) + ' ')
	print('\033[' + str(pausetop + 4) + ';' + str(pauseleft) + 'H' + ' ' + chr(9553) + '            ' + chr(9553) + ' ')
	print('\033[' + str(pausetop + 5) + ';' + str(pauseleft) + 'H' + ' ' + chr(9562) + chr(9552)*12 + chr(9565) + ' ')
	print('\033[' + str(pausetop + 6) + ';' + str(pauseleft) + 'H' + ' '*16)

	system('play -q audio/pause.ogg')

#####################################################################################################
#######################################################-- main function calls -######################
#####################################################################################################

classic_board = intro()
system('reset')

plan_the_board()
build_the_board()

place_blocks()
place_boxes()

beasts = place_pawns(beasts, beast_cnt)
monsters = place_pawns(monsters, monster_cnt)
#eggs = place_pawns(eggs, egg_cnt)

player = place_pawns(player, 1 )



#####################################################-- main loop threads --#########################

############################-- the main loop that waits for key presses


def takeInput():
	global debug, keypress, player

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
		elif keypress == ord('b'):
			if debug == True:
				debug = False
			else:
				debug = True
		elif keypress == ord(' '):
			while (keypress == ord(' ')):
				keypress = stdscr.getch()
				player[1]['tug'] = not player[1]['tug']
				if (keypress != ord(' ')):
					tugspan = keypress # logs the present direction to compare for direction change
					while (tugspan == keypress): # this ensures the player has pull function until direction key changes.
						move_player(keypress)
						player[1]['tug'] = True
						keypress = stdscr.getch()				
		if keypress != ord(' '):
			player[1]['tug'] = False
			move_player(keypress)
# start the thread that runs the input loop

threading.Thread(target=takeInput).start()



############################-- the main game clock and print loop


while(True):
	if keypress == ord('q'):
		system('reset')
		exit()
	elif keypress == ord('p'):
		pause()
		while(keypress == ord('p')):
			sleep(.05)
	else:
		system('clear')
		if beasts[0]['frame'] == beasts[0]['frames']:
			beasts[0]['frame'] = 0
		else:
			beasts[0]['frame'] += 1
		if monsters[0]['frame'] == monsters[0]['frames']:
			monsters[0]['frame'] = 0
		else:
			monsters[0]['frame'] += 1
		move_dist_enemies(beasts)
		print_board(board, True)
	sleep(lcd_time)
