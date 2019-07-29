import curses
from os import system
from time import sleep

keyNum = 0;


stdscr = curses.initscr() 
stdscr.keypad(1)
stdscr.refresh()
	

while(True):
    sleep(.05)
    keypress = stdscr.getch()
    system('echo \'' + str(keypress) + '\' >> level.txt')

system('reset')
