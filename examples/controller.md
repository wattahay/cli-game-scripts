I have an example key mapping in the beast.py file, with the title: XBOX.

It uses the y-u-i-o keys, although the keys are somewhat arbitrary.

There are instructions below on how to do it.

### **AntiMicroX** with an **XBOX 360** Controller

This is a very specific example of an XBOX 360 controller, using another application to map a conroller to basic keyboard keys.

AntiMicroX is found on Linux in the conventional app centers.

There is an [example xbox360.gamecontroller.amgp file](https://github.com/wattahay/cli-game-scripts/blob/master/examples/xbox360.gamecontroller.amgp) to import into AntiMicroX for the mapping that exists in the beast.py file.


### Controller Mapping

```       
              LB                   RB         
           /======\_____________/======\            Up: D^   (to i) 105,73
      LT  /  /--\      ___        (Y)   \  RT     Down: Dv   (to u) 117,85
          | | LS |  B ( G ) S  (X)   (B) |       Right: D>   (to o) 111,79
          |  \__/      ---        (A)    |        Left: D<   (to y) 121,89
         |         ^         /--\         |       Pull: A    (to Shift)
         |       < D >      | RS |        |       Exit: LB   (to ESC)
        |          v         \__/          |      Exit: RB   (to Ctrl-c)
        |         ________________         |     Pause: X    (to p)
        |       _/                \_       |     Start: GD/B (to Spacebar)
        \     _/                    \_     /       Tab: Y    (to Tab)
         \___/                        \___/
```

### Manual Steps

1. Install and test AntiMicroX to ensure it works with your setup.
2. Decide which keys to map to your controller, and map the controller.
3. Use getkeycodes.py to get the keyboard codes for UP, DOWN, LEFT, RIGHT, pull UP, pull DOWN, pull LEFT, pull RIGHT
4. Edit the beast.py file to include an entry for the keycodes you use.
5. Run the beast.py script with the newly created option, or select the option in settings. Example: `python3 beast.py -k:XBOX`

> **Note:** If you map existing keys used by beast.py, then you do not have to get any keyboard key codes. You can still change the name of an entry in the beast.py file.

### Using the provided example.

1. In AntiMicroX, import the [example xbox360.gamecontroller.amgp file](https://github.com/wattahay/cli-game-scripts/blob/master/examples/xbox360.gamecontroller.amgp) file.
2. Locate the KYBD array, which contains a commented out XBOX dictionary.
3. Remove the pound sign to uncomment the line.
4. Add a pound sign to another line to keep the options at 3.

> **Note:** The 1st 3 options are used if all 4 are uncommented.

```
KYBD = [
{"title":"wasd", 	"K_UP":119, "K_DOWN":115, "K_RIGHT":100, "K_LEFT":97,  "PK_UP":87,  "PK_DOWN":83,  "PK_RIGHT":68,  "PK_LEFT":65},
{"title":"XBOX",  	"K_UP":105, "K_DOWN":117, "K_RIGHT":111, "K_LEFT":121, "PK_UP":73,  "PK_DOWN":85,  "PK_RIGHT":79,  "PK_LEFT":89},
#{"title":"arrows",	"K_UP":259, "K_DOWN":258, "K_RIGHT":261, "K_LEFT":260, "PK_UP":337, "PK_DOWN":336, "PK_RIGHT":402, "PK_LEFT":393},
{"title":"hjkl", 	"K_UP":107, "K_DOWN":106, "K_RIGHT":108, "K_LEFT":104, "PK_UP":75,  "PK_DOWN":74,  "PK_RIGHT":76,  "PK_LEFT":72}
]
```
