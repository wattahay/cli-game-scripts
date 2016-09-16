# ubuntu: sudo apt-get install python3 colorama
from colorama import Fore, Back, Style
from time import sleep
import os

sub = 8329
egg = (chr(11052) + chr(sub))
brokegg = (chr(65857) + chr(65856))
monster = Fore.RED + Style.NORMAL + chr(9568) + chr(9571) + Style.RESET_ALL


while(True):
	os.system('clear')
	if (sub >= 8321):
		print(chr(11052) + chr(sub) + '\n\n')
		sub -= 1
	elif (sub < 8321) & (sub >= 8320):
		print(brokegg + '\n\n')
		sub -= 1
	elif (sub < 8320):
		print(monster + '\n\n')
		sub = 8329
		sleep(2)
	sleep(4)
	
