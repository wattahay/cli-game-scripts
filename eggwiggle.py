import curses
from random import randint
import sys
import os
from time import sleep
import tty
import threading
import re

board_rows = 9
board_cols = 9
board = []

BOX ='\033[32m' +chr(9618) + chr(9618) +'\033[0m'
EGG = '\033[37m' + chr(11052) + chr(32) +'\033[0m'
BAKGRD = '  '




def build_board():
	for i in range(board_rows):
		board.append([])
		for ic in range(board_cols):
			board[i].append(BAKGRD)




def print_board():
	os.system('tput civis')
	for i in range(board_rows):
		print(''.join(board[i]))




def fill_board():
	for i in range(board_rows):
		for ic in range(board_cols):
			if (i % 3 == 2) & (ic % 2 == 0):
				board[i][ic] = BOX
			elif (i % 3 == 1) & (ic % 2 == 1):
				board[i][ic] = EGG


def wiggle_tr():
	for i in range(2):
		os.system('tput cup 1 14')
		print('  ')
		os.system('tput cup 1 13')
		print(EGG)
		sleep(.05)
		os.system('tput cup 1 13')
		print('  ')
		os.system('tput cup 1 14')
		print(EGG)
		sleep(.05)
		os.system('tput cup 1 14')
		print('  ')
		os.system('tput cup 1 15')
		print(EGG)
		sleep(.05)
		os.system('tput cup 1 15')
		print('  ')
		os.system('tput cup 1 14')
		print(EGG)
		sleep(.05)
	os.system('tput cup 14 1 && printf "    " && tput cup 14 1')

def wiggle_tl():
	for i in range(2):
		os.system('tput cup 1 2')
		print('  ')
		os.system('tput cup 1 1')
		print(EGG)
		sleep(.05)
		os.system('tput cup 1 1')
		print('  ')
		os.system('tput cup 1 2')
		print(EGG)
		sleep(.05)
		os.system('tput cup 1 2')
		print('  ')
		os.system('tput cup 1 3')
		print(EGG)
		sleep(.05)
		os.system('tput cup 1 3')
		print('  ')
		os.system('tput cup 1 2')
		print(EGG)
		sleep(.05)
	os.system('tput cup 14 1 && printf "    " && tput cup 14 1 ')

def wiggle_ll():
	for i in range(2):
		os.system('tput cup 7 2')
		print('  ')
		os.system('tput cup 7 2')
		print(EGG)
		sleep(.05)
		os.system('tput cup 7 1')
		print('  ')
		os.system('tput cup 7 1')
		print(EGG)
		sleep(.05)
		os.system('tput cup 7 1')
		print('  ')
		os.system('tput cup 7 3')
		print(EGG)
		sleep(.05)
		os.system('tput cup 7 3')
		print('  ')
		os.system('tput cup 7 2')
		print(EGG)
		sleep(.05)
	os.system('tput cup 14 1 && printf "    "  && tput cup 14 1 ')

def wiggle_lr():
	for i in range(2):
		os.system('tput cup 7 14')
		print('  ')
		os.system('tput cup 7 13')
		print(EGG)
		sleep(.05)
		os.system('tput cup 7 13')
		print('  ')
		os.system('tput cup 7 14')
		print(EGG)
		sleep(.05)
		os.system('tput cup 7 14')
		print('  ')
		os.system('tput cup 7 15')
		print(EGG)
		sleep(.05)
		os.system('tput cup 7 15')
		print('  ')
		os.system('tput cup 7 14')
		print(EGG)
		sleep(.05)
	os.system('tput cup 14 1 && printf "    " && tput cup 14 1  ')




build_board()
fill_board()
os.system('clear')
print_board()

keypress = ''
print('\n\'tl\': top left   \'tr\': top right \n\'ll\': lower left  \'lr\': lower right')
os.system('tput cup 14 1')
while (True):
	keypress = input()
	if keypress == 'tr':
		wiggle_tr()
	elif keypress == 'tl':
		wiggle_tl()
	elif keypress == 'll':
		wiggle_ll()
	elif keypress == 'lr':
		wiggle_lr()
	else:
		break
	

input()	

os.system('tput cvvis')
	
		
