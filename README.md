Python(3) script based on the 1984 DOS game, BEAST

Setup
=====

a. Install and run xfce4-terminal in Ubuntu/Mint
1. On the git page, click the green Clone/Download button to get the .zip file
2. Extract the zipped files, maintaining the same directory structure
3. Give the beast.py file executable permissions: chmod +x beast.py
4. In the terminal, change directory to that of the executable (or else audio will not work)
5. Run the game: ./beast.py

Controls
========

* 'esc'...........quit game / exit the options menu
* 'tab'...........enter options menu / switch tabs in options menu
* 'p'.............pause
* 'b'.............debug stats
* arrows..........move
* ctrl............pull blocks
* 'r'.............restore screen / resized terminal


For Best Results
================

* Terminal Emulator Ranking
	* xfce4-terminal - Liberation Mono - Tango Color Scheme
	* guake - Liberation Mono - Tango Color Scheme
	* gnome-terminal - Liberation Mono - Tango Color Scheme
	* konsole
	* xterm
	* "uxterm" (lxterm)
	* "Terminator" (x-terminal-emulator)

 Most terminals have profiles you can create for individual applications.

* Font Ranking
 	* Liberation Mono (closest to original)
	* Noto Mono
	* WenQuanYi Micro Hei Mono
	* Free Mono (this is good in Gnome-terminal)
	* Ubuntu Mono
 	* DeJaVu Sans Mono
 	* Tlwg Mono looks . . . interesting
* Alter font sizes for varied results
* Run in a termainal that can:
	* change font size (changes board size)
	* change font
	* change color schemes
	* make user profiles


File Tweaks
===========

Edit these settings in the beast.py file to change the game. 
(These settings might be added to an options menu in the future.

* lcd_time
	* change this if there are issues with flickering or player speed
	* lower (faster) than .02 is usually counter-productive
	* higher (slower) than .07 makes for clunkly gameplay


Advanced Tweaks
===============
* use xset to change keyboard delay




