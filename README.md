Linux Python script based on the **[1984 DOS game, BEAST](https://github.com/wattahay/cli-game-scripts/wiki)**. (Specifically it is created in Fedora.)

Control keys can be set to h-j-k-l to practice **Vim key muscle memory**!

**Visual elements** are Unicode characters drawn using **[terminal escape sequences](https://github.com/wattahay/cli-game-scripts/wiki/Inline-Cursor-Movement)**.

### Gameplay

Pawns kill you when they reach you.

Move blocks around to squash the enemy pawns. Get points. Clear the level to progress.

There is a large point penalty, and a level panalty, for losing 5 lives.

```
Beasts...................red 'H's
	> Beasts can be squashed using regular green blocks
Monsters.................double-lined red 'H's
	> Monsters must be squashed against yellow/orange blocks
Eggs.....................hatch into monsters
	> Eggs can only be moved using green blocks.
	> Like Monsters, they must be squashed against yellow or orange blocks.
	> New eggs appear when Monsters group together
Green Blocks (Boxes).....can be pushed and pulled
Yellow/Orange Blocks.....immovable
	> Orange blocks destroy green blocks that are pushed into them.
	> Orange blocks take a life if you walk into them
	> Walking into an orange block gives you some green boxes if you are low.
```

### Runs in Linux Terminal

1. On the git page, click the green Clone/Download button to get the .zip file
2. Extract the zipped files, maintaining the same directory structure
3. Set up a terminal with an increased font size, and a **Dark Tango** color palette
4. In the terminal, cd into the newly unzipped directory
5. Set executable permissions on beast.py
   * `chmod +x beast.py`
6. Run the script
   * `./beast.py`

> If making the script executable does not work, then try: `python3 beast.py`

> After you run the game, the intro should show up. At this point you can adjust the terminal size, and the board will center itself.

### To Compile a Portable Version

This creates a portable executable for your architecture about 9MB.

```
pip3 install --upgrade --user pyinstaller
pyinstaller -F --add-data audio:audio beast.py
cd dist/
./beast
```

### Script Options

Example: `./beast.py -w:54 -h:30 -t -k:hjkl`

```
-i................information and instructions mode
-c................create/use the default config file
	> -c.i..............include information comments in new config file
	> -c:file.ini.......create/use config with custom filename
	> -c.i:file.ini.....include information comments in new config file
-t................transparent background
-f................fitted to terminal
	> -f:2..............additional padding
-k:hjkl...........key controls
	> options: "wasd", "arrows", "hjkl"
-w:50.............custom game width
	> 2-digit number (option trumps fitted width)
-h:30.............custom game height
	> 2-digit number (option trumps fitted height)
```

See: [Terminal Fitting Options](https://github.com/wattahay/cli-game-scripts/wiki/Terminal-Fitting-Options)



### Controls

```
spacebar......enter level / exit settings
esc...........quit the game
ctrl-c........quit the game
tab...........enter options menu / switch tabs in options menu
p.............pause
b.............debug stats
shift.........pull blocks
r.............restore screen for a resized terminal
```

The direction keys can be customized in a config file created using -c options. The getkeycodes.py script identifies codes for the keys you want to use.

Also see: [Adding Controller Option](https://github.com/wattahay/cli-game-scripts/blob/master/examples/controller.md)


### Best Terminals

1. gnome-terminal
2. kitty
3. blackbox-terminal
4. xfce4-terminal
5. konsole
6. xterm
7. "uxterm" (lxterm)
8. "Terminator" (x-terminal-emulator)

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



