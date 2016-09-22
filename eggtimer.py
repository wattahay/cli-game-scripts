from colorama import Fore, Back, Style
from time import sleep
import os
import re

sub = 8329
brokegg = (chr(65857) + chr(65856))
monster = Fore.RED + Style.NORMAL + chr(9568) + chr(9571) + Style.RESET_ALL

reggex = re.compile('\u2B2C.')
space = ''

while(space != monster):
	os.system('clear')
	if (sub >= 8321):
		egg = (chr(11052) + chr(sub))
		space = egg
		sub -= 1
	elif (sub < 8321) & (sub >= 8320):
		space = brokegg
		sub -= 1
	elif (sub < 8320):
		space = monster
		sub = 8329
	print('\n'*10)
	if (re.match(reggex, space)):
		print('\r' + ' '*19 + space + '    ...It\'s an egg.' + '\n'*10)
	elif (space == brokegg):
		print('\r' + ' '*19 + space + '       Something is hatching!\n' + '\n'*10)
	else:
		print('\r' + ' '*19 + space + '       It\'s a Monster!!' + '\n'*10)
	sleep(4)
	
