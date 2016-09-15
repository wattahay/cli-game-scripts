from colorama import Fore, Back, Style
from random import randint
import sys
import os
from time import sleep
import termios
import tty
import threading

##########################################################################################
####################################--global variables--##################################
##########################################################################################
beast_speed = 1.5	# seconds between enemy moves
monster_speed = 1.5	# seconds between enemy moves

board_rows = 22
board_cols = 42
left_margin = ' '

block_cnt = 10
box_cnt = randint(210,225)
beast_cnt = 4
monster_cnt = 0
egg_cnt = 0

lives = 5
kills = 0
level = 1
score = 0

debug = False

lcd_time = .07	# frame-rate of entire game (CONSTANT)
beast_steps = int(beast_speed / lcd_time)	# global inter-enemy asyncronicity
monster_steps = int(monster_speed / lcd_time)	# global inter-enemy asyncronicity

beast_stepper = 0
monster_stepper = 0

beast_seeds = []	# individual asyncronicity loopers
monster_seeds = []	# individual asyncronicity loopers

beasts = []
monsters = []
eggs = []
player = []

board = []
move = ''

dirlist = ['u','d','l','r','ul','ur','dl','dr']

###################-- formatted game-piece ascii characters

bakgrd_chr = '  ' 
border_chr = Back.YELLOW + Style.NORMAL + '  ' + Style.RESET_ALL
box_chr = Fore.GREEN + chr(9618) + chr(9618) + Style.RESET_ALL
beast_chr = Fore.RED + Style.NORMAL + chr(9500) + chr(9508) + Style.RESET_ALL
monster_chr = Fore.RED + Style.NORMAL + chr(9568) + chr(9571) + Style.RESET_ALL
player_chr = Fore.BLUE + chr(9664) + chr(9654) + Style.RESET_ALL
egg_chr = Fore.WHITE + Style.BRIGHT + chr(9675) + chr(9675) + Style.RESET_ALL

###################--initialize board

# BUILDS a blank board
def build_blank_board(): #{
	for rowi in range(board_rows):
		board.append([])
		for coli in range(board_cols):
			board[rowi].append([])
			board[rowi][coli] = bakgrd_chr
#}





def print_board(): #{
	for rowi in range(board_rows):
		print('\r' + left_margin + ''.join(board[rowi]))
	print('\r' + left_margin + '   SCORE: ' + str(score) + '   LIVES: ' + str(lives) + '    LEVEL: ' + str(level)) 
	if(debug):
		print('\nPlayer: ' + str(player) + '\nBeasts: ' + str(beasts) + '\nBSeeds: ' + str(beast_seeds) + '\nBeast Stepper: ' + str(beast_stepper) + '\nBeast Steps: ' + str(beast_steps)) 


###############################################################
####################################--inkey--##################
###############################################################

def inkey(key_buffer):
	fd = sys.stdin.fileno()
	remember_attributes = termios.tcgetattr(fd)
	tty.setraw(sys.stdin.fileno())
	character = sys.stdin.read(key_buffer)
	termios.tcsetattr(fd, termios.TCSADRAIN, remember_attributes)
	return character



###############################################################
####################################--board--##################
###############################################################

def draw_borders():
	for rowi in range(board_rows):
		for coli in range(board_cols):
			if(rowi == 0) | (rowi == (board_rows - 1)) | (coli == 0) | (coli == (board_cols - 1)):
				board[rowi][coli] = border_chr
				 





###############################################################
####################################--block_cnt--#################
###############################################################
###############################################################


# clears the board before and after each level and game
def clear_level():
	for rowi in range(board_rows):
		for coli in range(board_cols):
			if(((rowi > 0) & (rowi <= (board_rows - 2))) & ((coli > 0) & (coli <= (board_cols - 2)))):
				board[rowi][coli] = bakgrd_chr
	


# fills the board with appropriate number of yellow block_cnt
def draw_blocks(): #{
	row_ranges = [[1,2],[3,4],[5,6],[7,8],[9,10],[11,12],[13,14],[15,16],[17,18],[19,20]]
	col_ranges = [[1,4],[5,8],[9,12],[13,16],[17,20],[21,24],[25,28],[29,32],[33,36],[37,40]]
	step = 9 
	rowi = 0
	coli = 0

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
		board[rowi][coli] = border_chr
		step -= 1
		del col_ranges[col_range_index]
		del row_ranges[row_range_index]


	step = 0
	while(step < box_cnt):
		row = randint(1, board_rows - 1)
		col = randint(1, board_cols - 1)
		if(board[row][col] == bakgrd_chr):
			board[row][col] = box_chr
			step += 1
	

#}

			
#############################################################################
##################################################-- place the pieces -- ####
#############################################################################
def place_pieces(piece, count, char):
	step = 0
	while(step < count):
		row = randint(1, board_rows - 1)
		col = randint(1, board_rows - 1)
		if(board[row][col] == bakgrd_chr):
			board[row][col] = char
			piece.append(dict({'ro':row, 'co':col}))
			step += 1
			if(char == beast_chr):
				beast_seeds.append(randint(0, (beast_steps - 1)))
			elif(char == monster_chr):
				monster_seeds.append(randint(0, (monster_steps - 1)))

	return piece
	


def unlist_piece(index, char):
	if (char == beast_chr):
		del beasts[index]
		del beast_seeds[index]
	elif (char == monster_chr):
		del monsters_chr[index]
		del beast_seeds[index]
	elif (char == egg_chr):
		del eggs_chr[index]
	

##############################################################################
##############################################-- move pieces --##############
##############################################################################




def move_piece(godir, piece, index, char, tug):
	global bakgrd_chr, box_chr
	row = piece[index]['ro']
	col = piece[index]['co']
	fow = row
	fol = col
	rtug = row
	ctug = col
	if godir == 'l': # LEFT
		fow = row
		fol = col - 1
		rtug = row
		ctug = col + 1
	elif (godir == 'r'): # RIGHT
		fow = row
		fol = col + 1
		rtug = row
		ctug = col - 1
	elif (godir == 'd'): # DOWN
		fow = row + 1
		fol = col
		rtug = row - 1
		ctug = col
	elif (godir == 'u'): # UP
		fow = row - 1
		fol = col
		rtug = row + 1
		ctug = col
	elif (godir == 'ul'): # D - UP n LEFT
		fow = row - 1
		fol = col - 1
	elif (godir == 'ur'): # D - UP n RIGHT
		fow = row - 1
		fol = col + 1
	elif (godir == 'dl'): # D - DOWN n LEFT
		fow = row + 1
		fol = col - 1
	elif (godir == 'dr'): # D - DOWN n RIGHT
		fow = row + 1
		fol = col + 1
	if (board[fow][fol] == bakgrd_chr):
		board[fow][fol] = char 
		if (tug) & (board[rtug][ctug] == box_chr):
			board[rtug][ctug] = bakgrd_chr
			board[row][col] = box_chr
		else:
			board[row][col] = bakgrd_chr
		piece[index]['ro'] = fow
		piece[index]['co'] = fol
	



def move_dist_enemies(): #{
	global beast_seeds, monster_seeds, beast_stepper, monster_stepper
	# pick one of the beasts to move
	for bi in range(len(beasts)):
		if beast_seeds[bi] == beast_stepper:
			dirindex = randint(0, len(dirlist) - 1) # randomly pick a direction to go
			direction = dirlist[dirindex]
			move_piece(direction, beasts, bi, beast_chr, False)
#}



def move_player():
	global player, move, player_chr
	if move == 'w':
		move_piece('u', player, 0, player_chr, False)
	elif move == 'a':
		move_piece('l', player, 0, player_chr, False)
	elif move == 's':
		move_piece('d', player, 0, player_chr, False)
	elif move == 'd':
		move_piece('r', player, 0, player_chr, False) 




def player_pull():	
	global player, move, player_chr 
	while(move == ' '):
		move = inkey(1)
		if (move == 'w'):
			move_piece('u', player, 0, player_chr, True)
		elif (move == 'a'):
			move_piece('l', player, 0, player_chr, True)
		elif (move == 's'):
			move_piece('d', player, 0, player_chr, True)
		elif (move == 'd'): 
			move_piece('r', player, 0, player_chr, True)

###################################################################
###################################################################



build_blank_board()
#input()
#print_board()
draw_borders()
#input()
#print_board()
draw_blocks()
#input()
#print_board()
beasts = place_pieces(beasts, beast_cnt, beast_chr)
#input()
#print_board()
#monsters = place_pieces(monsters, monster_cnt, monster_chr)
#input()
#print_board()
#eggs = place_pieces(eggs, egg_cnt, egg_chr)
#input()
#print_board()
player = place_pieces(player, 1, player_chr)
#input()
#print_board()





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
			player_pull()
		else:
			move_player()




move = 0 
t = threading.Thread(target=takeInput)
t.start()





while(True):
	os.system('clear')
	if move == 'q':
		exit()
	move_dist_enemies()
	print_board()
	if beast_stepper == beast_steps:
		beast_stepper = 0
	else:
		beast_stepper += 1
	if monster_stepper == monster_steps:
		monster_stepper = 0
	else:
		monster_stepper += 1
	sleep(lcd_time)
	

