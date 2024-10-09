Linux-Only Python script based on the **1984 DOS game, BEAST**. (Specifically it is created in Fedora.)

This is a very rudimentary script, but it might be entertaining to have a look at.

The game is crude, but it is **not that far from the original**. It cam be addictive.

There is an options to replace the arrow controls with **Vim keys (h,j,k,l)**, which can be used to **train your Vim muscle memory** if nothing else.

**Visual elements** are Unicode characters drawn using terminal escape sequences.

### Setup

A. Set up a terminal with an increased ~26 font size (Monospace), and a Dark Tango color palette.
1. On the git page, click the green Clone/Download button to get the .zip file
2. Extract the zipped files, maintaining the same directory structure
3. Give the beast.py file executable permissions: chmod +x beast.py
4. In the terminal, change directory to that of the executable (or else audio will not work)
5. Run the game: ./beast.py

### Controls

* 'esc'...........quit game / exit the options menu
* 'tab'...........enter options menu / switch tabs in options menu
* 'p'.............pause
* 'b'.............debug stats
* arrows..........move
* ctrl............pull blocks
* 'r'.............restore screen / resized terminal

### Gameplay

Pawns kill you when they reach you.

Move blocks around to squash the enemy pawns. Get points. Clear the level to progress.

* **Beasts** are red 'H's
	* Beasts can be squished using regular green blocks
* **Monsters** are double-lined red 'H's
	* Monsters must be squished right against yellow or orange blocks
* **Eggs** hatch into monsters
	* Eggs must be pushed using green blocks, into yellow or orange blocks
* Green blocks can be **pushed and pulled**
* Yellow and orange blocks are immovable
	* Orange blocks destroy/explode green blocks that are pushed into them.
	* **Orange blocks kill you** if you walk into them


### Settings & Controls

* You have brief chances to access the settings before every level
	* (Press the **Tab** key right after/before each level.)


### Best Terminals

* Terminal Emulator Ranking
	* xfce4-terminal - Liberation Mono - Tango Color Scheme
	* guake - Liberation Mono - Tango Color Scheme
	* gnome-terminal - Liberation Mono - Tango Color Scheme
	* konsole
	* xterm
	* "uxterm" (lxterm)
	* "Terminator" (x-terminal-emulator)

 Most terminals have profiles you can create for individual applications.

* Use a **dark tango** color palette, and make the background darker if needed.
* Font Ranking
	* RedHat Mono
	* Noto Mono
	* WenQuanYi Micro Hei Mono
	* Free Mono (this is good in Gnome-terminal)
	* Ubuntu Mono
 	* Liberation Mono
 	* DeJaVu Sans Mono
 	* Tlwg Mono looks . . . interesting
* Alter font sizes for varied results

### Most Lacking Features

* persistent settings storage
* start script with custom level settings profile
* access the right settings at any time
* better navigation controls between menu/gameplay/program

### Next Gameplay Features

* Better egg hatching
* Better chaotic movement control for pawns
* Better default general gameplay balance
* More gradual levels

### Post Next Features

* Line-of-site movement for pawns
* Added form to block placement


