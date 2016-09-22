import curses
from random import randint
#import sys
import os
from time import sleep
#import tty
import threading
import re
#################################
#####-- get tty sizes --#########################
#############################################################
ttyRows, ttyCols = os.popen('stty size', 'r').read().split()######
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

beast_speed = 1.5	# seconds between enemy moves
monster_speed = 1.5	# seconds between enemy moves
egg_speed = 4		# seconds between countdowns

min_incubate = 5	# minimum time before eggs start counting down
max_incubate = 30	# maximum time before eggs start counting down

lcd_time = .06
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
BLOCK =		       		'\033[43m' +         		'  ' + 				'\033[0m'
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

#}






def print_board(): #{

	global ttyCols, top_margin, left_margin, score, lives, level, board_rows, board_cols


	# Hide the cursor
	os.system('tput civis')
	
	bottom_margin = top_margin - 3

	#     |
	#     V
	#     |
	#     V
	#     |
	#     V
	#     |
	#     V
	####-- Print Top Margin	
	print('\n'*top_margin)
	
					#########################################
					#					#
	####-- Print Left Margin ->->-> #	H				#
	####-- Print Board		#		H	<>		#
	for rowi in range(board_rows):	#					#
		print('\r' + ' '*left_margin + ''.join(board[rowi]))		#
					#				H	#
					#					#
					#	H				#
					#########################################
	####-- Print Game Stats ------>  Score: 200  Lives: 4  Level: 3
	print('\r' + ' '*left_margin + '   SCORE: ' + str(score) + '   LIVES: ' + str(lives) + '    LEVEL: ' + str(level)) 

	####-- Print Debug Stats
	if(debug):
		print(
			'\n\r Player: ' + str(player) +
			'\n\rBeasts: ' + str(beasts) +
			'\n\rBeast Stepper: ' + str(beasts[0]['frame'])
		 ) 


	



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




def move_pawns(godir, pieces, index):
	global BAKGRD, BOX, MVU, MVL, MVR, MVD, MVUL, MVUR, MVDL, MVDR
	
	char = pieces[0]['chr']
	row = pieces[index]['ro']
	col = pieces[index]['co']
	fow = row
	fol = col
	rtug = row
	ctug = col
	if godir == MVL: # LEFT
		fow = row
		fol = col - 1
		rtug = row
		ctug = col + 1
	elif (godir == MVR): # RIGHT
		fow = row
		fol = col + 1
		rtug = row
		ctug = col - 1
	elif (godir == MVD): # DOWN
		fow = row + 1
		fol = col
		rtug = row - 1
		ctug = col
	elif (godir == MVU): # UP
		fow = row - 1
		fol = col
		rtug = row + 1
		ctug = col
	elif (godir == MVUL): # D - UP n LEFT
		fow = row - 1
		fol = col - 1
	elif (godir == MVUR): # D - UP n RIGHT
		fow = row - 1
		fol = col + 1
	elif (godir == MVDL): # D - DOWN n LEFT
		fow = row + 1
		fol = col - 1
	elif (godir == MVDR): # D - DOWN n RIGHT
		fow = row + 1
		fol = col + 1
	if (board[fow][fol] == BAKGRD):
		board[fow][fol] = char 
		if (pieces[index]['tug']) & (board[rtug][ctug] == BOX):
			board[rtug][ctug] = BAKGRD
			board[row][col] = BOX
		else:
			board[row][col] = BAKGRD
		pieces[index]['ro'] = fow
		pieces[index]['co'] = fol



def move_dist_enemies(pieces): #{
	# pick one of the beasts to move
	for i in range(1, len(pieces)):
		if pieces[i]['stag'] == pieces[0]['frame']:
			dirindex = randint(0, len(DIR_LIS) - 1) # randomly pick a direction to go
			direction = DIR_LIS[dirindex]
			move_pawns(direction, pieces, i)
#}


#





#################################3
################################################3
def inkey(key_buffer):###############-- inkey --##########3
	fd = sys.stdin.fileno()#################################3
	remember_attributes = termios.tcgetattr(fd)#################3
	tty.setraw(sys.stdin.fileno())#################################3
	character = sys.stdin.read(key_buffer)###########################3
	termios.tcsetattr(fd, termios.TCSADRAIN, remember_attributes)####3
	return character##################################################3
#########################################################################3
#####################################################################3

def move_player(mv):	

	global player, MVU, MVL, MVD, MVR

	if (mv == curses.KEY_UP):
		move_pawns(MVU, player, 1)
	elif (mv == curses.KEY_LEFT):
		move_pawns(MVL, player, 1)
	elif (mv == curses.KEY_DOWN):
		move_pawns(MVD, player, 1)
	elif (mv == curses.KEY_RIGHT):
		move_pawns(MVR, player, 1)




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
		os.system('clear')
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
			os.system('clear')
		elif (introquestion == 'c'):
			classic = True 
			os.system('clear')
		elif (introquestion == 'q'):
			os.system('clear')
			exit()

	return classic

#####################################################################################################
#######################################################-- main function calls -######################
#####################################################################################################

classic_board = intro()
os.system('reset')

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
			os.system('clear')
			exit()
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
					move_player(keypress)
		elif keypress != ord(' '):
			move_player(keypress)

# start the thread that runs the input loop

t = threading.Thread(target=takeInput)
t.start()



############################-- the main game clock and print loop

while(True):
	os.system('clear')
	if keypress == ord('q'):
		os.system('reset')
		exit()
	move_dist_enemies(beasts)
	print_board()
	if keypress == ord('p'):
		input()
	if beasts[0]['frame'] == beasts[0]['frames']:
		beasts[0]['frame'] = 0
	else:
		beasts[0]['frame'] += 1
	if monsters[0]['frame'] == monsters[0]['frames']:
		monsters[0]['frame'] = 0
	else:
		monsters[0]['frame'] += 1
	sleep(lcd_time)



