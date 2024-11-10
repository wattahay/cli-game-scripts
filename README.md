### Notes

Linux-Only Python script based on the **1984 DOS game, BEAST**. (Specifically it is created in Fedora.)

This is a rudimentary script, but it might be entertaining to have a look at.

The game is actually **not that far from the original**. 

Probably the best appeal for a wide use-case for this would be a quick way to practice **Vim key muscle memory** on the command line. (The direction controls can be assigned to **h,j,k,l**.)

**Visual elements** are Unicode characters drawn using terminal escape sequences.

### Setup

Set up a terminal with an increased ~26 font size, and a Dark Tango color palette.
1. On the git page, click the green Clone/Download button to get the .zip file
2. Extract the zipped files, maintaining the same directory structure
3. Give the beast.py file executable permissions: chmod +x beast.py
4. In the terminal, change directory to that of the executable (or else audio will not work)
5. Run the game: ./beast.py

### Initial Game Start

1. As stated above: run the game with ./beast.py (or python3 beast.py)
2. Wait for the start screen to load.
3. Press 'tab' to enter the settings
4. Choose your control keys. (the change takes place immediately)
5. Press 'tab' to see and change upcoming level setup or pawn speeds
6. Press 'esc' to escape the settings, and enter the next level

**Note:** The pull key changes between 'shift' and 'ctrl' depending on the chosen direction keys.

### Controls

* 'esc'...........quit game / exit the options menu
* 'tab'...........enter options menu / switch tabs in options menu
* 'p'.............pause
* 'b'.............debug stats
* arrows..........move
* ctrl/shift......pull blocks
* 'r'.............restore screen for a resized terminal

### Gameplay

Pawns kill you when they reach you.

Move blocks around to squash the enemy pawns. Get points. Clear the level to progress.

There is a large point penalty, and a level panalty, for losing 5 lives.

The game has no breaks or saves (yet). You can press pause wit 'p'. You have a brief, passing chance to press 'tab' for settings changes before/after each level.

* **Beasts** are red 'H's
	* Beasts can be squished using regular green blocks
* **Monsters** are double-lined red 'H's
	* Monsters must be squished right against yellow or orange blocks
* **Eggs** hatch into monsters
	* **To kill eggs**, they must be pushed into yellow/orange blocks, using green blocks
	* New eggs might appear in the distance when Monsters swarm around you
* **Green blocks** can be **pushed and pulled**
* **Yellow/orange** blocks are immovable
	* Orange blocks destroy/explode green blocks that are pushed into them.
	* **Orange blocks kill you** if you walk into them


### Settings & Controls

* You have brief chances to access the settings before every level
	* (Press the **Tab** key right after/before each level.)


### Best Terminals

1. gnome-terminal
2. kitty
3. xfce-terminal
4. konsole
5. xterm
6. "uxterm" (lxterm)
7. "Terminator" (x-terminal-emulator)

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
* Alter font sizes for higher resolution screens

### Most Lacking Features

* keyboard code calibrator (unless the keyboard function changes)
* persistent settings storage
* custom level files
* start script with custom level settings profile
* better navigation controls between menu/gameplay/program

### Next Gameplay Features

* Better egg hatching
	* Instead of eggs simply appearing in the distance, a Monster must leave the swarm, and walk over to lay it.
* Better chaotic movement control for pawns
* Better default general gameplay balance
* Better levels

### Post-Next Features

* Re-Write?
* Intermittent line-of-site movement for pawns
* Added form to block placement
* Design maps in a spreadsheet application
	* export/import as CSV file
* Simple map doorways (not panning)
	* This is because walls are used to kill and stop things.
 	* Doorways can be discovered behind blocks
  	* Other items can be found, like:
  		* keys
  	 	* lives
  	  	* anything


