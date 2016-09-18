# pybeast
Python(3) script based on the 1984 DOS game, BEAST
* The game was created in Linux Mint, using xfce4-terminal
* The only special installation is colorama (sudo apt-get install python3 colorama)


###################################################
############-- For Best Results --#################
###################################################

* Use Mono fonts (Ubuntu Mono looks pretty good)
* Temporarily change font sizes for bigger players
* Run in a termainal that can:
	* change between Mono fonts
	* change color schemes
	* change font sizes
* Set max_board_size to smaller than 50 by 50 to prevent screen glitching



###################################################
##################-- Setup --######################
###################################################
(The game runs in the terminal)

1. run an update
	* run: sudo apt-get update
2. run: sudo apt-get install python3 colorama
3. download or save the pybeast.py
4. navigate to the folder of the downloaded file
5. run: chmod +x pybeast.py
6. run: python3 pybeast.py
7. set the board option to 'c' for classic mode or 't' for dynamic terminal sizing


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





