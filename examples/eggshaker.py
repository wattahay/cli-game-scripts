from time import sleep
from os import system

#######################################################################################

# This file demonstrates how to clear and print characters from their tty location
# rather than re-printing the entire array of the board every split second


# this is about fixing speed and screen glitches in the terminal and console


# this method fixes the console issue

#######################################################################################

# the shaker() method shows how the \033[<x>;<y> ANSI sequence allows printing to a specific location on the screen
# by first moving to that position and printing over it with spaces
# then moving to the position again and printing over it.

board_rows = 9
board_cols = 9
board = []

BOX ='\033[32m' +chr(9618) + chr(9618) +'\033[0m'
EGG = '\033[37m' + chr(11052) + chr(32) +'\033[0m'
BAKGRD = '  '

row = 0
col = 0

def build_board():
	for i in range(board_rows):
		board.append([])
		for ic in range(board_cols):
			board[i].append(BAKGRD)




def print_board():
	system('tput civis')
	for i in range(board_rows):
		print(''.join(board[i]))




def fill_board():
	for i in range(board_rows):
		for ic in range(board_cols):
			if (i % 3 == 2) & (ic % 2 == 0):
				board[i][ic] = BOX
			elif (i % 3 == 1) & (ic % 2 == 1):
				board[i][ic] = EGG



def shaker(row, col):
	shakes = int(input('shakes: '))
	for i in range(shakes):
		sleep(.05)
		print('\033[' + str(row) + ';' + str(col) + 'H  ')
		col -= 1
		print('\033[' + str(row) + ';' + str(col) + 'H' + EGG)
		sleep(.05)
		print('\033[' + str(row) + ';' + str(col) + 'H  ')
		col += 1
		print('\033[' + str(row) + ';' + str(col) + 'H' + EGG)
		sleep(.05)
		print('\033[' + str(row) + ';' + str(col) + 'H  ')
		col += 1
		print('\033[' + str(row) + ';' + str(col) + 'H' + EGG)
		sleep(.05)
		print('\033[' + str(row) + ';' + str(col) + 'H  ')
		col -= 1
		print('\033[' + str(row) + ';' + str(col) + 'H' + EGG)
	print('\033[15;1H            \033[14;1H          \033[13;2H')



build_board()
fill_board()
system('clear')
print_board()

keypress = ''
print('\n\'tl\': top left   \'tr\': top right \n\'ll\': lower left  \'lr\': lower right')
print('\033[13;2H')
while (True):
	sleep(1)
	keypress = input('corner: ')
	if keypress == 'tr':
		shaker(2, 15)
	elif keypress == 'tl':
		shaker(2, 3)
	elif keypress == 'll':
		shaker(8, 3)
	elif keypress == 'lr':
		shaker(8, 15)
	else:
		system('tput cvvis')
		exit()
	


	
		
