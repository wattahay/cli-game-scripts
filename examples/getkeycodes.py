import curses
from os import system

stdscr = curses.initscr()
stdscr.keypad(1)
stdscr.refresh()
curses.curs_set(False)

try:
    while True:
        keypress = stdscr.getch()
        print('\033[0K\033[HCode: ' + str(keypress) + '          \033[1E\033[2K')
except KeyboardInterrupt:
        system('reset')
