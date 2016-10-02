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

beast_speed = 1.0	# seconds between enemy moves
monster_speed = 1.0	# seconds between enemy moves
egg_speed = 4		# seconds between countdowns

min_incubate = 5	# minimum time before eggs start counting down
max_incubate = 30	# maximum time before eggs start counting down


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

eggsub = 8329			# unicode key for subscript 9 (8328 = 8, and so on)
egg2nd = 32			# unicode key for a space character 
REGGX = re.compile('\u2B2C.') 	# use re.match(REGGX, char) to see if a piece is an egg

# (ANSI styles)	 FG   + 	BG   + 		Style +		Characters +			Reset
BAKGRD = 							'  ' 
BLOCK =		       		'\033[43m' +	       		'  ' + 				'\033[0m'
KILLBLOCK = 	'\033[31m'	'\033[43m' + 			chr(9618) + chr(9618) + 	'\033[0m'
BOX = 		'\033[32m' +					chr(9618) + chr(9618) +		'\033[0m'
EGG = 		'\033[37m' +					chr(11052) + chr(egg2nd) + 	'\033[0m'
BEAST = 	'\033[31m' +					chr(9500) + chr(9508) +		'\033[0m'
MONSTER = 	'\033[31m' +					chr(9568) + chr(9571) +		'\033[0m'
PLAYER = 	'\033[34m' +					chr(9664) + chr(9654) +		'\033[0m'
# http://wiki.bash-hackers.org/scripting/terminalcodes

###################################-- Pawn Classes (Dictionaries)
##################################-- Pawn Lists 

# pawn lists dynamically grows and shrink with 

beasts = [{
	'frames': ((int(beast_speed / lcd_time)) - 1),
	'frame':0,
	'chr': BEAST 
	}]

monsters = [{
	'frames': ((int(beast_speed / lcd_time)) - 1),
	'frame':0,
	'chr': MONSTER
	}]

eggs = [{
	'frames': ((int(beast_speed / lcd_time)) - 1),
	'frame':0,
	'chr': EGG
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


#	intro = board
#	roster = board
#	controls = board
#	info = board
#
#	global intro, roster, controls, info

#}






def print_board(board_array, stats): #{

	global ttyCols, top_margin, left_margin, score, lives, level, board_rows, board_cols


	# Hide the cursor
	system('tput civis')
	

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
		print('\rPlayer: ' + str(player) + '\n')
		print('\rBeasts: ' + str(beasts[0]))
		for i in range(1, len(beasts)):
			print('\r\tBeast ' + str(i) + ' :' + str(beasts[i]))
		 

	



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
			

	
#############################################################################
##################################################-- place the pieces -- ####
#############################################################################



def place_pawns(pawns, count):

	pawn = pawns[0]['chr']
	step = 0 
	while(step < count):
		row = randint(1, (board_rows - 1))
		col = randint(1, (board_cols - 1))
		if(board[row][col] == BAKGRD):
			board[row][col] = pawn 
			pawns.append({'ro':row, 'co':col, 'tug':False, 'stg':0 })
			step += 1
			if (pawn != PLAYER):
				pawns[step]['stg'] = randint(1, (pawns[0]['frames']))

	return pawns
	


##############################################################################
##############################################-- move pieces --##############
##############################################################################






def kill_player():

	global lives, board, stop_take_input

	lives -= 1
	del player[1]
	place_pawns(player, 1)
	
	def audio_kill():
		system('play -q audio/loss2.ogg')
	
	threading.Thread(target=audio_kill).start()

	###############################################


def move_enemies(pawns): #{

	global board, player, MVU, MVL, MVD, MVR, MVUL, MVUR, MVDL, MVDR, MOVES

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

			priority_odds = [	#197
				[150, False],	#150		**********************************************
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
					board[pawns[pwni]['ro']][pawns[pwni]['co']] = pawns[0]['chr']
					kill_player()
					breakloop = True
					break
				# else if the priority move is not available, then mark it as unavailable
				elif ((board[ ((pawns[pwni]['ro']) + (MOVES[move_priority[priopti]]['ra'])) ][ ((pawns[pwni]['co']) + (MOVES[move_priority[priopti]]['ca'])) ]) == BAKGRD ):
					priority_odds[priopti][1] = True
					system('echo \"Priority ' + str(priopti) + ': ' + str((priority_odds[priopti][1])) + '\" >> move_lists.txt')
				else:
					priority_odds[priopti][1] = False
					system('echo \"Priority ' + str(priopti) + ': ' + str((priority_odds[priopti][1])) + '\" >> move_lists.txt')
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


#def move_dist_enemies(pieces): #{
#	# pick one of the beasts to move
#	for i in range(1, len(pieces)):
#		if pieces[i]['stag'] == pieces[0]['frame']:
##			dirindex = randint(0, len(DIR_LIS) - 1) # randomly pick a direction to go
#			direction = DIR_LIS[dirindex]
#			move_pawns(direction, pieces, i)
#}


#



def move_player(tap):	

	global player, board, MOVES, MVU, MVL, MVD, MVR, BAKGRD, BOX
	
	move = ''

	if (tap == curses.KEY_UP):
		#player[1]['mv'] = MVU
		move = MVU
	elif (tap == curses.KEY_LEFT):
		#player[1]['mv'] = MVL
		move = MVL
	elif (tap == curses.KEY_DOWN):
		#player[1]['mv'] = MVD
		move = MVD
	elif (tap == curses.KEY_RIGHT):
		#player[1]['mv'] = MVR
		move = MVR

	fow = player[1]['ro'] + MOVES[move]['ra'] 
	fol = player[1]['co'] + MOVES[move]['ca'] 
	rtug = player[1]['ro'] - (MOVES[move]['ra'])
	ctug = player[1]['co'] - (MOVES[move]['ca'])


	if ( board[fow][fol] == BAKGRD):
		board[fow][fol] = player[0]['chr'] 
		if ((player[1]['tug'] == True) & (board[rtug][ctug] == BOX)):
			board[rtug][ctug] = BAKGRD
			board[player[1]['ro'] ][ player[1]['co'] ] = BOX
		else:
			board[player[1]['ro'] ][ player[1]['co'] ] = BAKGRD
		player[1]['ro'] = fow
		player[1]['co'] = fol





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

place_blocks(BLOCK)
place_boxes()

#monsters = place_pawns(monsters, monster_cnt)
beasts = place_pawns(beasts, beast_cnt)
#eggs = place_pawns(eggs, egg_cnt)

player = place_pawns(player, 1 )





#############################################################################
##################################################-- take input func -- #####
#############################################################################
	


def take_input():
	global debug, keypress, player, stop_take_input
	
	stop_take_input = False
	stdscr = curses.initscr() 
	curses.cbreak()
	stdscr.keypad(1)
	stdscr.refresh()

	while(True):
		keypress = stdscr.getch()
		if (stop_take_input):
			while(stop_take_input):
				sleep(lcd_time)
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


#########################################################################################################
threading.Thread(target=take_input).start()  ###############-- the main game clock and print loop --#####
#########################################################################################################



while(True):
	if keypress == ord('q'):
		system('reset')
		exit()
	elif keypress == ord('p'):
		pause()
		while(keypress == ord('p')):
			sleep(.5)
		game_pause = 0
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
		move_enemies(beasts)
		print_board(board, True)
	sleep(lcd_time)


