# pybeast
Python(3) script based on the 1984 DOS game, BEAST
* The game was created in Linux Mint, using xfce4-terminal


###################################################
############-- For Best Results --#################
###################################################
* xfce4-terminal produces drastically better font styling than gnome-terminal
* Use Mono fonts (Ubuntu Mono looks pretty good)
 	* Ubuntu Mono
 	* Liberation Mono
 	* DeJaVu Sans Mono
 	* FreeMono (ok)
 	* Tlwg Mono looks . . . interesting
* Enlarge font sizes for varied results
* Run in a termainal that can:
	* change between Mono fonts
	* change color schemes
	* change font sizes
* Set max_board_size to 90 by 90 to prevent screen glitching



###################################################
##################-- Setup --######################
###################################################
(The game runs in the terminal)

1. download or save the pybeast.py
2. navigate to the folder of the downloaded file
3. run: chmod +x pybeast.py
4. run: python3 pybeast.py
5. set the board option to 'c' for classic mode or 't' for dynamic terminal sizing


###################################################
##################-- Tweeks --#####################
###################################################
Tweek settings in the file
* Useful global variables are placed 50 rows in
* alter enemy speed by 10s of a second
* alter game frame_rate with the variable: lcd_time
	* .1 is about the slowest
	* .05 - .08 makes for better player movement
	* too fast makes the game flicker and glitch
* max_play_rows and max_play_cols prevent dynamic boards from getting unruly
* there are settings for level 1 enemies and point adjustments





