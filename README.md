Linux Python script based on the **[1984 DOS game, BEAST](https://github.com/wattahay/cli-game-scripts/wiki)**. (Specifically it is created in Fedora.)

Control keys can be set to h-j-k-l to practice **Vim key muscle memory**!

**Visual elements** are Unicode characters drawn using **[terminal escape sequences](https://github.com/wattahay/cli-game-scripts/wiki/Inline-Cursor-Movement)**.

### Gameplay

Pawns kill you when they reach you.

Move blocks around to squash the enemy pawns. Get points. Clear the level to progress.

There is a large point penalty, and a level panalty, for losing 5 lives.

```
Beasts...................red 'H's
	Beasts can be squashed using regular green blocks
Monsters.................double-lined red 'H's
	Monsters must be squashed against yellow/orange blocks
Eggs.....................hatch into monsters
	Eggs can only be moved using green block.
	Like Monsters, they must be squashed against yellow or orange blocks.
	New eggs appear in the distance when Monsters swarm around you
Green Blocks.............can be pushed and pulled
Yellow/Orange Blocks.....immovable
	Orange blocks destroy green blocks that are pushed into them.
	Orange blocks kill you if you walk into them
```

### Runs in Linux Terminal

1. On the git page, click the green Clone/Download button to get the .zip file
2. Extract the zipped files, maintaining the same directory structure
3. Set up a terminal with an increased font size, and a Dark Tango color palette
4. Run the game: `python3 beast.py`

### Script Options

Example: `python3 beast.py -w:54 -h:30 -t -k:hjkl`

```
-t.........transparent background
-f.........fitted to terminal
-f:2.......additional padding
	1-to-5 accommodates terminal spacing differences
-k:hjkl....key controls
	options: "wasd", "arrows", "hjkl"
-w:50......custom game width
	2-digit number (option trumps fitted width)
-h:30......custom game height
	2-digit number (option trumps fitted height)
```

See: [Terminal Fitting Options](https://github.com/wattahay/cli-game-scripts/wiki/Terminal-Fitting-Options)

### Controls

```
spacebar......enter level / exit settings / toggle pulling blocks
esc...........quit the game
ctrl-c........quit the game
tab...........enter options menu / switch tabs in options menu
p.............pause
b.............debug stats
shift.........pull blocks
r.............restore screen for a resized terminal
```

Player movement control has 3 options in the settings menu, or as script options.

```
wasd
arrows
hjkl
```
These options can be customized in the beast.py file, in the KYBD array. The getkeycodes.py script identifies the codes for the keys you want to use.

Also see: [Adding Controller Option](https://github.com/wattahay/cli-game-scripts/blob/master/examples/controller.md)

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



