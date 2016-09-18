from colorama import Fore, Back, Style
from random import randint
import sys
import os
from time import sleep
import termios
import tty
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

max_play_rows = 40	# alter max game height here
max_play_cols = 70 	# alter max game width here
max_beast_cnt = 10	# alter max beasts here

##################################-- starting game statistics

beast_cnt = 4 		# starting beasts	
lives = 5		# starting lives

squish_boxes = False	# boxes shuv into nothing against blocks
wall_hit_death = False	# player dies against walls

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

lcd_time = .07		# frame-rate of entire game (CODISTADIT)

###################################################################################
##################################-- formatted character constants--###############
###################################################################################

eggsub = 8329			# unicode key for subscript 9 (8328 = 8, and so on)
egg2nd = 32			# unicode key for a space character 
REGGX = re.compile('\u2B2C.') 	# use re.match(REGGX, char) to see if a piece is an egg

EGG = 		Fore.WHITE + 	Style.BRIGHT + 	chr(11052) + chr(egg2nd) + Style.RESET_ALL
BAKGRD = 					'  ' 
BORDER =	Back.YELLOW + 	Style.NORMAL + 	'  ' + 			Style.RESET_ALL
BOX = 		Fore.GREEN + 			chr(9618) + chr(9618) + Style.RESET_ALL
BEAST = 	Fore.RED + 	Style.NORMAL + 	chr(9500) + chr(9508) + Style.RESET_ALL
MONSTER = 	Fore.RED + 	Style.NORMAL + 	chr(9568) + chr(9571) + Style.RESET_ALL
PLAYER = 	Fore.BLUE + 			chr(9664) + chr(9654) + Style.RESET_ALL

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

U = 'U'
D = 'D'
L = 'L'
R = 'R'
UL = 'UL'
UR = 'UR'
DL = 'DL'
DR = 'DR'

DIR_LIS = (U, D, L, R, UL, UR, DL, DR)

####################################################################################################
move = '' ###################################################-- frame-scale globals-- ##############
####################################################################################################

###################################-- Piece Dictionaries

#beast_steps = int(beast_speed / lcd_time) - 1		# number of frames in between beast moves
#monster_steps = int(monster_speed / lcd_time) - 1	# number of frames in between monser moves
#egg_steps = int(egg_speed / lcd_time) - 1		# number of frames in between egg stages


beasts = [{'chr': BEAST, 'steps':((int(beast_speed / lcd_time)) - 1), 'frame': 0}] 
# 'ro' = row of each item
# 'co' = col of each item
# 'fow' = potential move
# 'fol' = potential move
# 'seed' = the interval at which each beast moves
# 'mv' = direction of travel
monsters = [{'chr': MONSTER, 'steps':((int(beast_speed / lcd_time)) - 1), 'frame': 0}]
# 'ro' = row of each item
# 'co' = col of each item
# 'fow' = potential move
# 'fol' = potential move
# 'seed' = the interval at which each monster moves 
# 'mv' = direction of travel
eggs = [{'chr': EGG, 'steps':((int(beast_speed / lcd_time)) - 1), 'frame': 0}]
# 'ro' = row of each item
# 'co' = col of each item
# 'fow' = potential move
# 'fol' = potential move
# 'seed' = the interval at which each egg hatches
# 'sub' = the unicode number of the subscript countdown
# 'tmr' = the countdown until each egg hatches
# 'mv' = direction of travel
push = False
tug = False
player = [{'chr':PLAYER}, {'mv':'', 'push':False, 'tug': False, 'ro':0, 'co':0}]
# 'ro' = row
# 'co' = col
# 'fow' = potential move
# 'fol' = potential move
# 'mv' = direction of travel

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
min_play_rows = round((play_rows + 6) / 3)
min_play_cols = round((play_cols + 6) / 3)
board_rows = play_rows + 2
board_cols = play_cols + 2
debug = False

def plan_the_board(): #{

	global top_margin, left_margin, board_rows, board_cols, play_rows, play_cols, min_play_rows, min_play_cols, max_play_rows, max_play_cols, stat_rows, debug_rows, ttyCols, screen_rows, screen_cols

	set_margin = 2
	fill_margin = 4 # This prevents fill boards from completely removing margins
	stat_rows = 2
	debug_rows = 5
	used_rows = 0
	used_cols = 0
	 
	if (classic_board):
		top_margin = int((screen_rows - board_rows - stat_rows) / 2)
		left_margin = int((ttyCols - board_cols*2) / 2)
	else:
		# this condition tests to see if the board is in the middle range of the fill size
		# if it is true, then the board should fill the terminal, but have a slim boarder
		if ((screen_rows <= (max_play_rows + fill_margin)) & (screen_rows > (min_play_rows + fill_margin))):
			play_rows = int((screen_rows - fill_margin) / 3) * int(3)
			board_rows = play_rows + 2
			used_rows = play_rows + fill_margin + stat_rows
			top_margin = int((screen_rows - used_rows) / 2)
		else: # if the board is either small or huge 
			play_rows = int((screen_rows - set_margin) / 3) * int(3)
			board_rows = play_rows + 2
			used_rows = board_rows + set_margin + stat_rows
			top_margin = int((screen_rows - used_rows) / 2)


		if ((screen_cols <= (max_play_cols + fill_margin)) & (screen_cols > (min_play_cols + fill_margin))):
			play_cols = int((screen_cols - fill_margin) / 3) * int(3)
			board_cols = play_cols + 2
			used_cols = play_cols + fill_margin
			left_margin = int((ttyCols - used_cols*2) / 2)
		else: # if the board is either small or huge 
			play_cols = int((screen_cols - set_margin) / 3) * int(3)
			board_cols = play_rows + 2
			used_cols = board_cols + set_margin
			left_margin = int((ttyCols - used_cols*2) / 2)


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
				board[rowi][coli] = BORDER

	

#}


def print_board(): #{

	global ttyCols, top_margin, left_margin, score, lives, level, board_rows, board_cols

	print('\n'*top_margin)
	for rowi in range(board_rows):
		print('\r' + ' '*left_margin + ''.join(board[rowi]))
	print('\r' + ' '*left_margin + '   SCORE: ' + str(score) + '   LIVES: ' + str(lives) + '    LEVEL: ' + str(level)) 
	if(debug):
		print('\n\r' + ' '*left_margin + 'Player: ' + str(player) + '\n\rBeasts: ' + str(beasts) + '\n\rBSeeds: '  + '\n\rBeast Stepper: ' + str(beasts[0][stpr]) ) 



###############################################################
####################################--block_cnt--##############
###############################################################


# fills the board with appropriate number of yellow block_cnt
def place_blocks(): #{

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
	else:
		row_loop = int(play_rows / 3)
		col_loop = int(play_cols / 3)
		if row_loop < col_loop:
			step = row_loop - 1
		else:
			step = col_loop - 1
		
		for i in range(row_loop):
			row_ranges.append([i, i + 2])

		for i in range(col_loop):
			col_ranges.append([i, i + 2])

	
	while(step >= 0):
		# 1st, randomly select a row range to use
		row_range_index = randint(0, step)
		# 2nd, randomly select a number from that range to be the row index of the block
		rowi = randint(row_ranges[row_range_index][0], row_ranges[row_range_index][1])
		# 1st randomly select a col range to use
		col_range_index = randint(0, step)
		# 2nd randomly select a number from that range to be the col index of the block
		coli = randint(col_ranges[col_range_index][0], col_ranges[col_range_index][1])
		# Finally, set the board place equal to the yellow border color
		board[rowi][coli] = BORDER
		step -= 1
		del col_ranges[col_range_index]
		del row_ranges[row_range_index]
		
				
#}

def place_boxes():
	
	global play_rows, play_cols, classic_board

	if (classic_board):
		box_cnt = randint(210,225)
	else:
		prerange = int(play_rows * play_cols / 4)
		lower = prerange + int(prerange / 20)
		upper = prerange + (int(prerange / 20) * 2)
		box_cnt = randint(lower,upper)
	
	step = 1
	while(step < box_cnt):
		row = randint(1, (board_rows - 1))
		col = randint(1, (board_cols - 1))
		if(board[row][col] == BAKGRD):
			board[row][col] = BOX
		step += 1	


	
#############################################################################
##################################################-- place the pieces -- ####
#############################################################################



def place_pieces(pieces, count):

	pawn = pieces[0]['chr']
	step = 0 
	while(step < count):
		row = randint(1, (board_rows - 1))
		col = randint(1, (board_cols - 1))
		if(board[row][col] == BAKGRD):
			board[row][col] = pawn 
			pieces.append({'ro':row, 'co':col, 'tug':False})
			step += 1
			if(pawn == BEAST) | (pawn == MONSTER) | (pawn == EGG):
				pieces[step]['seed'] = randint(0, (pieces[0]['steps']))
	return pieces
	

	


##############################################################################
##############################################-- move pieces --##############
##############################################################################




def move_piece(godir, pieces, index):
	global BAKGRD, BOX, U, L, R, D, UL, UR, DL, DR
	
	char = pieces[0]['chr']

	row = pieces[index]['ro']
	col = pieces[index]['co']
	fow = row
	fol = col
	rtug = row
	ctug = col
	if godir == L: # LEFT
		fow = row
		fol = col - 1
		rtug = row
		ctug = col + 1
	elif (godir == R): # RIGHT
		fow = row
		fol = col + 1
		rtug = row
		ctug = col - 1
	elif (godir == D): # DOWN
		fow = row + 1
		fol = col
		rtug = row - 1
		ctug = col
	elif (godir == U): # UP
		fow = row - 1
		fol = col
		rtug = row + 1
		ctug = col
	elif (godir == UL): # D - UP n LEFT
		fow = row - 1
		fol = col - 1
	elif (godir == UR): # D - UP n RIGHT
		fow = row - 1
		fol = col + 1
	elif (godir == DL): # D - DOWN n LEFT
		fow = row + 1
		fol = col - 1
	elif (godir == DR): # D - DOWN n RIGHT
		fow = row + 1
		fol = col + 1
	if (board[fow][fol] == BAKGRD):
		board[fow][fol] = char 
		if (pieces[1]['tug'] == True) & (board[rtug][ctug] == BOX):
			board[rtug][ctug] = BAKGRD
			board[row][col] = BOX
		else:
			board[row][col] = BAKGRD
		pieces[index]['ro'] = fow
		pieces[index]['co'] = fol
	



def move_dist_enemies(pieces): #{
	# pick one of the beasts to move
	for bi in range(1, len(pieces)):
		if pieces[bi]['seed'] == pieces[0]['frame']:
			dirindex = randint(0, len(DIR_LIS) - 1) # randomly pick a direction to go
			direction = DIR_LIS[dirindex]
			move_piece(direction, pieces, bi)
#}


##################################3
################################################3
def inkey(key_buffer):###############-- inkey --##########3
	fd = sys.stdin.fileno()#################################3
	remember_attributes = termios.tcgetattr(fd)#################3
	tty.setraw(sys.stdin.fileno())#################################3
	character = sys.stdin.read(key_buffer)###########################3
	termios.tcsetattr(fd, termios.TCSADRAIDI, remember_attributes)####3
	return character##################################################3
#########################################################################3
#####################################################################3

def move_player():	

	global player, move, PLAYER

	while (move == ' '):
		player[1]['tug'] = True
		move = inkey(1)


	if (move == 'w'):
		move_piece(U, player, 1)
	elif (move == 'a'):
		move_piece(L, player, 1)
	elif (move == 's'):
		move_piece(D, player, 1)
	elif (move == 'd'): 
		move_piece(R, player, 1)




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
			+ 'Enter \'c\' to play a class sized board. . . '
			+ '\n\n\r' 
			+ ' '*int(ttyCols/2)
			)
		if (introquestion == 't'):
			classic = False
		elif (introquestion == 'c'):
			classic = True 
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

beasts = place_pieces(beasts, beast_cnt)
monsters = place_pieces(monsters, monster_cnt)
eggs = place_pieces(eggs, egg_cnt)

player = place_pieces(player, 1 )



#####################################################-- main loop threads --#########################

############################-- the main loop that waits for key presses

def takeInput():
	global debug, move
	while(True):
		move = inkey(1)
		if move == 'q':
			os.system('clear')
			exit()
		elif move == 'b':
			if debug == True:
				debug = False
			else:
				debug = True
		elif move == ' ':
			move_player()
		else:
			move_player()



# start the thread that runs the input loop

t = threading.Thread(target=takeInput)
t.start()



############################-- the main game clock and print loop

while(True):
	global move
	os.system('clear')
	if move == 'q':
		exit()
	move_dist_enemies(beasts)
	move_dist_enemies(monsters)
	move_dist_enemies(eggs)
	print_board()
	if move == 'p':
		input()
	if beasts[0]['frame'] == monsters[0]['steps']:
		beasts[0]['frame'] = 0
	else:
		beasts[0]['frame'] += 1
	if monsters[0]['frame'] == monsters[0]['steps']:
		monsters[0]['frame'] = 0
	else:
		monsters[0]['frame'] += 1
	sleep(lcd_time)



