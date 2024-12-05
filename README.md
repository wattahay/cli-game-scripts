### Notes

Linux-Only Python script based on the **[1984 DOS game, BEAST](https://github.com/wattahay/cli-game-scripts/wiki)**. (Specifically it is created in Fedora.)

This is a rudimentary script, but it might be entertaining to have a look at.

The game is actually **not that far from the original**. 

Probably the best appeal for a wide use-case for this would be a quick way to practice **Vim key muscle memory** on the command line. (The direction controls can be assigned to **h,j,k,l**.)

**Visual elements** are Unicode characters drawn using **[terminal escape sequences](https://github.com/wattahay/cli-game-scripts/wiki/Inline-Cursor-Movement)**.

### Gameplay

Pawns kill you when they reach you.

Move blocks around to squash the enemy pawns. Get points. Clear the level to progress.

There is a large point penalty, and a level panalty, for losing 5 lives.

```
Beasts...................red 'H's
	Beasts can be crushed using regular green blocks
Monsters.................double-lined red 'H's
	Monsters must be crushed right against yellow/orange blocks
Eggs.....................hatch into monsters
	To kill eggs, they must be pushed into yellow/orange blocks, using green blocks
	New eggs might appear in the distance when Monsters swarm around you
Green Blocks.............can be pushed and pulled
Yellow/Orange Blocks.....immovable
	Orange blocks destroy/explode green blocks that are pushed into them.
	Orange blocks kill you if you walk into them
```

### Runs in Linux Terminal

1. On the git page, click the green Clone/Download button to get the .zip file
2. Extract the zipped files, maintaining the same directory structure
3. Set up a terminal with an increased ~26 font size, and a Dark Tango color palette
4. Run the game: **python3 beast.py**

### Script Options

Example:
`python3 beast.py -w:54 -h:30 -t -k:hjkl`

```
-t.........transparent background
-f.........fitted to terminal
-f:2...additional padding
	1-to-5 accommodates terminal spacing differences
-k:hjkl....key controls
	options: "wasd", "arrows", "hjkl"
-w:50........custom game width
	2-digit number (option trumps fitted width)
-h:30......custom game height
	2-digit number (option trumps fitted height)
```

See: [Terminal Fitting Options](https://github.com/wattahay/cli-game-scripts/wiki/Terminal-Fitting-Options)

### Controls

```
spacebar......enter level / exit settings
esc...........quit the game
tab...........enter options menu / switch tabs in options menu
p.............pause
b.............debug stats
shift.........pull blocks
r.............restore screen for a resized terminal
```

Player movement control has 3 options in the settings menu:

```
w,a,s,d
arrow keys
h,j,k,l
```


### Change Many Default Settings in the beast.py Script

**Useful Variables**

If you open the script in a text editor, you will see the commented section: **Useful Variables**

```
Change level presets
Enemy kill points
Enemy speeds
Point loss penalty
Level penalty
Game clock speed
Default player controls setting
Enemies per level
Randomness of enemy movement
OS keyboard codes
```

### Best Terminals

1. gnome-terminal
2. kitty
3. xfce-terminal
4. konsole
5. xterm
6. "uxterm" (lxterm)
7. "Terminator" (x-terminal-emulator)

Most terminals have profiles you can create for unique purposes.

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

* persistent settings storage
* custom level files
* start script with custom level settings profile

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


