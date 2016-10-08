Python(3) script based on the 1984 DOS game, BEAST
RUNS BEST IN xfce4-terminal



###------- Setup -------
(The game runs in the terminal)

1. download beast.py
- download audio directory with files 
	* (the audio directory should be in the same directory as the beast.py file)
- in a terminal, navigate to the directory
- run: python3 beast.py


###----- Controls -----

* 'q'.............quit
* 'p'.............pause
* 'b'.............debug stats
* arrows..........move
* spacebar........pull blocks
* 'r'.............restore screen / resized terminal


###----- For Best Results -----

* Terminal Emulator Ranking
	* xfce4-terminal - Liberation Mono
	* guake - Liberation Mono
	* gnome-terminal - Free Mono
	* konsole
	* xterm
	* "uxterm" (lxterm)
	* "Terminator" (x-terminal-emulator)

 Most terminals have profiles you can create for individual applications.

* Font Ranking
	* Free Mono (this is good in Gnome-terminal)
 	* Liberation Mono (closest to original)
	* Noto Mono
	* WenQuanYi Micro Hei Mono
	* Ubuntu Mono
 	* DeJaVu Sans Mono
 	* Tlwg Mono looks . . . interesting
* Alter font sizes for varied results
* Run in a termainal that can:
	* change font size (changes board size)
	* change font
	* change color schemes
	* allow you to create user profiles
* change font sizes


###----- File Tweaks -----
Edit these seetings in the beast.py file to change the game. 
(These settings might be added to an options menu in the future.
	* lcd_time
		* change this if there are issues with flickering or player speed
		* lower (faster) than .02 is usually counter-productive
		* higher (slower) than .07 makes for clunkly gameplay
	* beast_speed - in seconds
	* monster_speed - in seconds
	* hatch_speed (countdown speed) - in seconds
	* beast_cnt - number of starting beasts

###--- Advanced Tweaks ---
	* use xset to change keyboard delay
		* alternatively, consider changing lcd_time
	* egg wait time algorithm


