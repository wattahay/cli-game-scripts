import curses
from random import randint
from os import system, popen
from time import sleep
import threading


##################################-- starting game statistics

beast_cnt = 4 		# starting beasts	
lives = 5		# starting lives

###############################

beast_speed = 1.5	# seconds between enemy moves
monster_speed = 1.1	# seconds between enemy moves
egg_speed = 3		# seconds between countdowns

##################################-- game scoring balance

level_scr = -50		# point loss if player loses level
beast_scr = 2		# points for killing beasts
egg_scr = 4		# points for killing eggs
monster_scr = 6		# points for killing monsters
death_scr = -10		# point loss for dying

##################################-- game speed

lcd_time = .04

####################################-- move constants

MOVES = {
 'U': {	'ra':-1,	'ca':0	}, 	# ra - "row adjustment"
 'D': {	'ra':1, 	'ca':0	},	# ca - "column adjustment"
 'L': {	'ra':0, 	'ca':-1	},
 'R': {	'ra':0, 	'ca':1	},
'UL': {	'ra':-1, 	'ca':-1	},
'UR': {	'ra':-1, 	'ca':1	},
'DL': {	'ra':1, 	'ca':-1	},
'DR': {	'ra':1, 	'ca':1	}
}

MVU  = 	'U'
MVD  = 	'D'
MVL  = 	'L'
MVR  = 	'R'
MVUL = 	'UL'
MVUR = 	'UR'
MVDL = 	'DL'
MVDR = 	'DR'

DIR_LIS = (MVU, MVD, MVL, MVR, MVUL, MVUR, MVDL, MVDR)

key_move = False
keypress = '' 
debug = False
countdown = 1
##################################-- formatted character constants


# (ANSI styles)	 FG   + 	BG   + 		Style +		Characters +			Reset
BAKGRD 	  =			'\033[40m' +			'  ' 
BLOCK 	  =       		'\033[43m' +	       		'  ' + 				'\033[0m'
KILLBLOCK = 	'\033[31m'	'\033[43m' + '\033[7m\033[2m' + chr(9618) + chr(9618) + 	'\033[0m'
BOX 	  =	'\033[32m' +	'\033[40m' +			chr(9618) + chr(9618) +		'\033[0m'
XPBOX 	  = 	'\033[32m' + 	'\033[40m' +	'\033[2m' +	chr(9618) + chr(9618) + 	'\033[0m'
BEAST 	  = 	'\033[31m' +	'\033[40m' +			chr(9500) + chr(9508) +		'\033[0m'
MONSTER   = 	'\033[31m' +	'\033[40m' +			chr(9568) + chr(9571) +		'\033[0m'
PLAYER    = 	'\033[34m' +	'\033[40m' +			chr(9664) + chr(9654) +		'\033[0m'
# http://wiki.bash-hackers.org/scripting/terminalcodes

eggsub = 8329			# unicode key for subscript 9 (8328 = 8, and so on)
egg2nd = 32			# unicode key for a space character 

def EGG(sub):
	return '\033[37m\033[40m\033[2m' + chr(11052) + '\033[1m' + chr(sub) + '\033[0m'


def deteggt(chegg):
	if (chegg[0:15] == '\033[37m\033[40m\033[2m' + chr(11052)): return True


###################################-- Pawn Classes (Dictionaries)
##################################-- Pawn Lists 

# pawn lists dynamically grows and shrink with 

beasts = [{
	'frames': ((int(beast_speed / lcd_time)) - 1),
	'frame':0,
	'chr': BEAST,
	'pnts': beast_scr 
	}]

monsters = [{
	'frames': ((int(monster_speed / lcd_time)) - 1),
	'frame':0,
	'chr': MONSTER,
	'pnts': monster_scr
	}]

eggs = [{
	'frames': ((int(egg_speed / lcd_time)) - 1),
	'frame':0,
	'incu_frames': (int(1 / lcd_time)), # incu_frames add up to 1 second
	'incu_frame': 0,
	'pnts': egg_scr
	}]

# 'sub'		updated digital unicode reference to subscript character
# 'wait'	randomized wait time before hatching countdown
player = [{
		'chr': PLAYER,
		'pnts': 10 
	}]
	
# 'tug'
# 'ro'		row
# 'co'		col
# 'stg'		"stagger" (frame of movement) compared to others
################################################################################################
####################################################################-- level 1 setup --#########
################################################################################################

monster_cnt = 0	# level 1 count
egg_cnt = 0	# level 1 count

kills = 0	# changes in-game
level = 0	# change in order to start on a specific level
score = 0	# in-game total score
points = 0	# in-game level points added at end of level


################################################################################################
board = [] #########################################################-- board setup --###########
blank_board = [] ###############################################################################
reset_board = [] ###########-- classic board size variables

play_rows = 20	# only change this in-game
play_cols = 40	# only change this in-game

block_cnt = 10	# level 1 count

######################################-- board dimensions
classic = True
left_margin = 0 
top_margin = 0
stat_rows = 3
board_rows = play_rows + 2
board_cols = play_cols + 2

def plan_the_board(): #{

	global save_top, save_left, top_margin, left_margin, board_rows, board_cols, play_rows, play_cols, stat_rows, stat_space, classic, ttyCols, ttyRows

	ttyRows, ttyCols = popen('stty size', 'r').read().split()
	ttyRows = int(ttyRows)
	ttyCols = int(ttyCols)
	screen_rows = ttyRows
	screen_cols = int(ttyCols / 2)

	if (screen_cols < 44) & (ttyRows < 28):	classic = False
	elif (ttyCols < 60) & (ttyRows < 20):
		print('This screen is impossibly small')
		sleep(3)
		system('reset')
	else: classic = True

	if (classic):
		board_rows = play_rows + 2
		board_cols = play_cols + 2
		top_margin = int((screen_rows - board_rows - stat_rows) / 2)
		left_margin = int((ttyCols - board_cols*2) / 2)
	else:
		board_rows = screen_rows - stat_rows
		board_cols = screen_cols
		top_margin = 0
		left_margin = 0

	save_top = top_margin # assigned for the debug feature 
	save_left = left_margin # assigned for the debug feature
	stat_space = int((board_cols * 2 - (4 * 14 )) / 5) # calculate this for the print_board function
	if stat_space < 0: stat_space = 0
	global stat_space, save_left, save_top
	#}

	

# BUILDS a blank board
def build_the_board(): #{
	global board_cols, board_rows

	screen_board = []

	for rowi in range(board_rows): # builds the board based on 'board_rows' and 'board_cols' which includes room for borders
		screen_board.append([])
		for coli in range(board_cols):
			screen_board[rowi].append([])
			screen_board[rowi][coli] = BAKGRD

	for rowi in range(board_rows): # draws the game boarders on the board
		for coli in range(board_cols):
			if(rowi == 0) | (rowi == (board_rows - 1)) | (coli == 0) | (coli == (board_cols - 1)):
				screen_board[rowi][coli] = BLOCK

	return screen_board
#}
board = build_the_board()
reset_board = build_the_board()
blank_board = build_the_board()


def print_board(board_array): #{

	global ttyCols, top_margin, left_margin, points, score, lives, level, board_rows, board_cols, save_top, save_left, stat_space

	print('\033[?25l\033[0m\033[' + str(top_margin)  + ';' + str(left_margin) + 'H\033[s')
						
	for rowi in range(board_rows + 1):	
		print('\033[u' + '\033[' + str(rowi) +  'B' + ''.join(board_array[rowi - 1]))		

	if (debug):
		print('\033[u' + '\033[' + str(len(board) + 4) + 'B' + '\rPlayer: ' + str(player) )
		for i in range(0, len(eggs)):
			if i == 0: print('\033[u' + '\033[' + str(len(board) + 6 + i) + 'B' + '\r\033[K\033[1B\033[K\033[1AEggs: ' + str(eggs[i]))
			else: print('\033[u' + '\033[' + str(len(board) + 6 + i) + 'B' + '\r\033[K\033[1B\033[K\033[1A\tEgg ' + str(i) + ': ' + str(eggs[i]))
		for i in range(0, len(beasts)):
			if i == 0: print('\033[u' + '\033[' + str(len(board) + len(eggs) + 7 + i) + 'B' + '\r\033[K\033[1B\033[K\033[1ABeasts: ' + str(beasts[i]))
			else: print('\033[u' + '\033[' + str(len(board) + len(eggs) + 7 + i) + 'B' + '\r\033[K\033[1B\033[K\033[1A\tBeast ' + str(i) + ': ' + str(beasts[i]))
		for i in range(0, len(monsters)):
			if i == 0: print('\033[u' + '\033[' + str(len(board) + len(eggs) + len(beasts) + 8 + i) + 'B' + '\r\033[K\033[1B\033[K\033[1AMonsters: ' + str(monsters[i]))
			else: print('\033[u' + '\033[' + str(len(board) + len(eggs) + len(beasts) + 8 + i) + 'B' + '\r\033[K\033[1B\033[K\033[1A\tMonster ' + str(i) + ': ' + str(monsters[i]))
		 
	print('\033[u' + '\033[' + str(len(board) + 2) + 'B' + '\033[' + str(stat_space) + 'C' + '\033[s' + chr(9477) + 
	' ' + 'TOTAL: ' + str(score)  + 	' ' + chr(9477) + '\033[u\033[' + str((stat_space + 14) * 1) + 'C' + chr(9477) + 
	' ' + 'TALLY: ' + str(points) + 	' ' + chr(9477) + '\033[u\033[' + str((stat_space + 14) * 2) + 'C' + chr(9477) + 
	' ' + 'LIVES: ' + str(lives)  +  	' ' + chr(9477) + '\033[u\033[' + str((stat_space + 14) * 3) + 'C' + chr(9477) + 
	' ' + 'LEVEL: ' + str(level)  +  	' ' + chr(9477)) 

	print('\033[H\033[8m')

##########################################################################################################
##############################################################################-- play audio function --###
##########################################################################################################

def play_audio(filename): system('aplay -q audio/' + filename + '.wav &')

##########################################################################################################
###############################################################################-- place the pieces -- ####
##########################################################################################################

def place_beasts(count):

	global beasts, board

	step = 0 
	while(step < count):
		row = randint(1, (board_rows - 1))
		col = randint(1, (board_cols - 1))
		if(board[row][col] == BAKGRD):
			board[row][col] = beasts[0]['chr'] 
			beasts.append({'ro':row, 'co':col, 'stg':0 })
			step += 1
			beasts[step]['stg'] = randint(1, (beasts[0]['frames']))

###########################################################################################

def hatch_monster(row, col):

	global monsters, board

	stagger = randint(1, (monsters[0]['frames']))	
	board[row][col] = MONSTER
	monsters.append({'ro':row, 'co':col,'stg':stagger })


def place_monsters(count):

	global monsters, board

	step = 0 
	while(step < count):
		row = randint(1, (board_rows - 1))
		col = randint(1, (board_cols - 1))
		if(board[row][col] == BAKGRD):
			hatch_monster(row, col)
			step += 1


###########################################################################################################
########################################################################################-- EGGS --#########
###########################################################################################################


def lay_egg(row, col):

	global monsters, beasts, eggs, board

	wait_frames = (len(eggs) + len(beasts) + len(monsters)) * eggs[0]['incu_frames'] * (randint(2, 6)) # seconds of wait time before egg starts counting down 
	stag = randint(1, eggs[0]['frames']) # the frame that the egg counts down on
	board[row][col] = EGG(32)
	eggs.append({'ro': row, 'co': col, 'wait': wait_frames, 'stg': stag, 'sub':32})


##############################################################################################


def place_eggs(count):

	global board

	step = 0 
	while(step < count):
		row = randint(1, (board_rows - 1))
		col = randint(1, (board_cols - 1))
		if(board[row][col] == BAKGRD):
			lay_egg(row, col)
			step += 1


#####################################################################

def hatch_eggs():
	# this function runs through all the eggs, and increments their time
	# it transition eggs from wait phase, to countdown, to Monster
	# wait_time is number of enemies at the time of creation times 4-16 (in seconds)
	# egg_speed is usually between 2 and 4 seconds. It is the time between countdown numbers
	global eggs, board, egg_speed, lcd_time, audio
	
	di = 0 # keeps track of index to accomodate for egg deletions

	if eggs[0]['frame'] == eggs[0]['frames']:
		eggs[0]['frame'] = 0
	else:
		eggs[0]['frame'] += 1
	if eggs[0]['incu_frame'] == eggs[0]['incu_frames']:
		eggs[0]['incu_frame'] = 0
	else:
		eggs[0]['incu_frame'] += 1
	# egg_speed, incu_frames, incu_frame, frames, frame, wait, stg
	# each egg: wait, stg
	for i in range(1, (len(eggs))):
		if (eggs[i - di]['wait'] > 0):
			eggs[i - di]['wait'] -= 1
		elif (eggs[i - di]['wait'] == 0) & (eggs[i - di]['sub'] == 32):
			eggs[i - di]['sub'] = 8329
		elif (eggs[i - di]['wait'] == 0) :
			if ((eggs[i - di]['stg'] == eggs[0]['frame']) & (eggs[i - di]['sub'] > 8320)):
				eggs[i - di]['sub'] -= 1
				board[eggs[i - di]['ro']][eggs[i - di]['co']] = EGG(eggs[i - di]['sub'])
			elif ((eggs[i - di]['sub'] == 8320) & (eggs[i - di]['stg'] == eggs[0]['frame'])):
				hatch_monster(eggs[i - di]['ro'], eggs[i - di]['co'])
				del eggs[i - di]
				play_audio('hatch')
				di += 1

##############################################################################
###############################################-- move pieces --##############
##############################################################################
def place_player():
	
	step = 0 
	while(step < 1):
		row = randint(1, (board_rows - 1))
		col = randint(1, (board_cols - 1))
		if(board[row][col] == BAKGRD):
			board[row][col] = player[0]['chr']
			step += 1
			player.append({'ro': row, 'co': col, 'tug': False })
			step += 1


def kill_player():

	global BAKGRD, player, lives, board

	board[ player[1]['ro'] ][ player[1]['co'] ] = BAKGRD
	lives -= 1
	del player[1]
	if lives > 0:
		place_player()

	play_audio('death')



def move_enemies(pawns): #{

	global board, player, MOVES

	if pawns[0]['frame'] == pawns[0]['frames']:
		pawns[0]['frame'] = 0
	else:
		pawns[0]['frame'] += 1

	move_priority = []
	move = ''

	breakloop = False
	lay = False
	likely_moves = []

	for pwni in range(1, (len(pawns))): # in a given frame, loops through all pawns in a list if the pawn is staggered to move in the present frame, the pawn moves to a space
		if (pawns[pwni]['stg'] == pawns[0]['frame']):
			rdistance = player[1]['ro'] - pawns[pwni]['ro'] # player row minus beast row
			cdistance = player[1]['co'] - pawns[pwni]['co'] # player column minus beast column

			if (rdistance == 0) | (cdistance == 0): # avoid division by zero
				distance_ratio = 0.0 # if the player is on the same row or column, the distance ratio is zero
			else:
				distance_ratio = rdistance / cdistance # division of row distance by column distance

			if ((rdistance < 0.0) & (cdistance < 0.0) & (distance_ratio >= .5) & (distance_ratio <= 2.0)):
				move_priority = [ MVUL, MVU, MVL, MVDL, MVUR, MVD, MVR, MVDR ] # UPPER LEFT range priorities
			elif ((rdistance < 0.0) & (cdistance > 0.0) & (distance_ratio <= -.5) & (distance_ratio >= -2.0)):
				move_priority = [ MVUR, MVU, MVR, MVUL, MVDR, MVL, MVDL, MVD ] # UPPER RIGHT range priorities
			elif ((rdistance > 0.0) & (cdistance > 0.0) & (distance_ratio >= .5) & (distance_ratio <= 2.0)):
				move_priority = [ MVDR, MVD, MVR, MVDL, MVUR, MVU, MVL, MVUL ] # DOWN RIGHT range priorities
			elif ((rdistance > 0.0) & (cdistance < 0.0) & (distance_ratio <= -.5) & (distance_ratio >= -2.0)):
				move_priority = [ MVDL, MVD, MVL, MVUL, MVDR, MVU, MVR, MVUR ] # DOWN LEFT range priorities
			elif ((rdistance < 0.0) & ((abs(distance_ratio) > 2.0) | (distance_ratio == 0.0))):
				move_priority = [ MVU, MVUL, MVUR, MVL, MVR, MVDL, MVDR, MVD ] # UPWARD range priorities
			elif ((cdistance > 0.0) & ((abs(distance_ratio) < .5) | (distance_ratio == 0.0))):
				move_priority = [ MVR, MVUR, MVDR, MVU, MVD, MVUL, MVDL, MVL ] # RIGHT range priorities
			elif ((rdistance > 0.0) & ((abs(distance_ratio) > 2.0) | (distance_ratio == 0.0))):
				move_priority = [ MVD, MVDL, MVDR, MVL, MVR, MVUL, MVUR, MVU ] # DOWNWARD range priorities
			elif ((cdistance < 0.0) & ((abs(distance_ratio) < .5) | (distance_ratio == 0.0))):
				move_priority = [ MVL, MVUL, MVDL, MVU, MVD, MVUR, MVDR, MVR ] # LEFT range priorities

			priority_odds = [	#145 total
				[98, False],	#98		**********************************************
				[18, False],	#18 or 36	* These values determine the odds of moves   *
				[18, False],	#18 or 36	* for an enemy if those moves are available. *
				[4, False],	#4 or 8		* If a move has an equivalent priority to    *
				[4, False],	#4 or 8		* another, but it is a box, then its odds    *
				[1, False],	#1 or 2		* are absorbed by the other.		     *
				[1, False],	#1 or 2		* DO NOT CHANGE NUMBER OF PRIORITIES!!!!!!!  *	
				[1, False]	#1		**********************************************
			]

			for priopti in range(8): 
				# if the first priority move is the player, then take that move
				if ((board[ ((pawns[pwni]['ro']) + (MOVES[move_priority[0]]['ra'])) ][ ((pawns[pwni]['co']) + (MOVES[move_priority[0]]['ca'])) ]) == PLAYER ):
					move = move_priority[0]
					board[pawns[pwni]['ro']][pawns[pwni]['co']] = BAKGRD
					pawns[pwni]['ro'] = player[1]['ro']
					pawns[pwni]['co'] = player[1]['co']
					kill_player()
					board[pawns[pwni]['ro']][pawns[pwni]['co']] = pawns[0]['chr']
					breakloop = True
					break
				# else if the priority move is not available, then mark it as unavailable
				elif ((board[ ((pawns[pwni]['ro']) + (MOVES[move_priority[priopti]]['ra'])) ][ ((pawns[pwni]['co']) + (MOVES[move_priority[priopti]]['ca'])) ]) == BAKGRD ):
					priority_odds[priopti][1] = True
				else:
					priority_odds[priopti][1] = False
				# if the pawn is a monster, and there is a monster or beast in the space, then lay an egg
				if ((pawns[0]['chr'] == MONSTER) & ((board[ ((pawns[pwni]['ro']) + (MOVES[move_priority[0]]['ra'])) ][ ((pawns[pwni]['co']) + (MOVES[move_priority[0]]['ca'])) ] == MONSTER) | (board[ ((pawns[pwni]['ro']) + (MOVES[move_priority[0]]['ra'])) ][ ((pawns[pwni]['co']) + (MOVES[move_priority[0]]['ca'])) ] == BEAST))):
					lay = True

			if (breakloop):
				break
	
			for prioddi in range(8): # loop through priorities to add them to likely_moves if available
				if (priority_odds[prioddi][1] == True): # if it is true that the priority move is a blank space, then loop through and fill out the likely_moves list
					for ti in range(priority_odds[prioddi][0]): # loop through by number in "priorities" loop, to fill out likely_moves list
						likely_moves.append(move_priority[prioddi])
				if ((prioddi == 2) | (prioddi == 4) | (prioddi == 6)):
					if ((not priority_odds[prioddi - 1][1]) & (priority_odds[prioddi][1] == True)):
						for ti in range(priority_odds[prioddi][0]):
							likely_moves.append(move_priority[prioddi])

			# the move is finally decided out of the available set in the list
			if (len(likely_moves) > 0):
				move = likely_moves[randint(0, (len(likely_moves)) - 1)]
				likely_moves = []
				# pawn row plus move row adjustment
				# pawn col plus move col adjustment
				board[ pawns[pwni]['ro'] + MOVES[move]['ra'] ][ pawns[pwni]['co'] + MOVES[move]['ca'] ] = pawns[0]['chr']
				# pawn row and pawn col = bakgrd
				board[ pawns[pwni]['ro'] ][ pawns[pwni]['co'] ] = BAKGRD
				# pawn[pawni] row and col = new row and col
				pawns[pwni]['ro'] = pawns[pwni]['ro'] + MOVES[move]['ra']
				pawns[pwni]['co'] = pawns[pwni]['co'] + MOVES[move]['ca']
#}


def push_tree(intent):

	global player, eggs, board, BLOCK, MOVES, BAKGRD, BOX, MVU, MVL, MVR, MVL, PLAYER

	push_eggs = []
 
	stnce_r = player[1]['ro']
	stnce_c = player[1]['co']
	tug_r = stnce_r - MOVES[intent]['ra']
	tug_c = stnce_c - MOVES[intent]['ca']
	intend_r = stnce_r + MOVES[intent]['ra']
	intend_c = stnce_c + MOVES[intent]['ca']
	def probe_r(p_ind):
		return player[1]['ro'] + p_ind * MOVES[intent]['ra']
	def probe_c(p_ind):
		return player[1]['co'] + p_ind * MOVES[intent]['ca']
	def wall_r(p_ind):
		return player[1]['ro'] + (p_ind + 1) * MOVES[intent]['ra']
	def wall_c(p_ind):
		return player[1]['co'] + (p_ind + 1) * MOVES[intent]['ca']
	def ram_r(p_ind):
		return player[1]['ro'] + (p_ind - 1) * MOVES[intent]['ra']
	def ram_c(p_ind):
		return player[1]['co'] + (p_ind - 1) * MOVES[intent]['ca']


	def push_move():

		global BOX, BAKGRD, PLAYER, player 

		for i in range(probe):
			board[ probe_r(probe - i) ][ probe_c(probe - i) ] = board[ probe_r(probe - 1 - i) ][ probe_c(probe - 1 - i) ]	# make board space same as preceeding space
		for i in range(len(push_eggs)):
			eggs[push_eggs[i]]['ro'] += MOVES[intent]['ra']
			eggs[push_eggs[i]]['co'] += MOVES[intent]['ca']
		if ((player[1]['tug']) & (board[tug_r][tug_c] == BOX)):
			board[tug_r][tug_c] = BAKGRD
			board[stnce_r][stnce_c] = BOX
		else:
			board[ player[1]['ro'] ][ player[1]['co'] ] = BAKGRD
		player[1]['ro'] = intend_r	
		player[1]['co'] = intend_c								# make player fol and fow the player
		board[intend_r][intend_c] = PLAYER						# move_player()
		
	
	def kill_enemy(pawns, row, col):

		global points, board

		del_index = 0

		for i in range(1, (len(pawns))):
			if ((pawns[i]['ro'] == row) & (pawns[i]['co'] == col)):
				del_index = i
				break
		del pawns[del_index]
		points += pawns[0]['pnts']

	probe = 2
	loop = True
	while (loop):

		space = board[probe_r(probe)][probe_c(probe)]
		ram_space = board[ram_r(probe)][ram_c(probe)]

		if (((probe_r(probe) != 0) & (probe_r(probe) != (len(board) - 1))) & ((probe_c(probe) != 0) & (probe_c(probe) != len(board[0]) - 1))):
			wall_space = board[wall_r(probe)][wall_c(probe)]
	
		if (space == BOX):		# if space is a box
			probe += 1 		# start loop over
		elif (space == BAKGRD): 		# if space is 
			push_move()
			loop = False
		elif (deteggt(space) == True): 	# if space is a egg
			system('echo \"egg\" >> eggfunc.txt')
			if (wall_space == BLOCK) | (wall_space == KILLBLOCK):	# if next block after egg is a border
				kill_enemy(eggs, probe_r(probe), probe_c(probe)) 			# del egg from global egg list
				play_audio('hatch')
				push_move()
				loop = False						# make space same as preceeding space
			elif ((wall_space == BAKGRD) | (wall_space == BOX)):
				for i in range(1, len(eggs)):
					if ((eggs[i]['ro'] == probe_r(probe)) & (eggs[i]['co'] == probe_c(probe))):
						push_eggs = [i] + push_eggs
				probe += 1
		elif (space == BLOCK):				# if space is a border
			loop = False
		elif (space == KILLBLOCK):	 		# if space is a killblock
			play_audio('flatten')
			push_move()
			board[probe_r(probe - 1)][probe_c(probe - 1)] = KILLBLOCK
			loop = False
		elif (space == BEAST): # if space is a beast
			if ((wall_space == KILLBLOCK) | (wall_space == BOX) | (wall_space == BLOCK)):
				kill_enemy(beasts, probe_r(probe), probe_c(probe))
				play_audio('squish')
				push_move()
			loop = False
		elif (space == MONSTER):# if space is a monster	
			if ((wall_space == KILLBLOCK) | (wall_space == BLOCK)):
				kill_enemy(monsters, probe_r(probe), probe_c(probe))
				play_audio('squish')
				push_move()		
			loop = False
			
		else:
			system('echo \"' + str(space) + '\" >> probe_space.txt')
			loop = False
	

def move_player(direction):
	global player, board, MOVES, BAKGRD, BOX, MVU, MVL, MVR, MVD

	pawns = player	
	index = 1
	char = player[0]['chr']
	row = player[1]['ro']
	col = player[1]['co']
	fow = row + MOVES[direction]['ra'] 
	fol = col + MOVES[direction]['ca']
	rtug = row - MOVES[direction]['ra']
	ctug = col - MOVES[direction]['ca']
	board[fow][fol] = char 
	if (pawns[index]['tug']) & (board[rtug][ctug] == BOX):
		board[rtug][ctug] = BAKGRD
		board[row][col] = BOX
	else:
		board[row][col] = BAKGRD
	player[index]['ro'] = fow
	player[index]['co'] = fol



def direct_move(tap_move):

	global player, MOVES, board

	space = board[player[1]['ro'] +  MOVES[tap_move]['ra'] ][ player[1]['co'] + MOVES[tap_move]['ca'] ]

	if (space == BAKGRD):
		move_player(tap_move)
	elif (space == BOX):
		push_tree(tap_move)
	elif (space == MONSTER) | (space == BEAST) | (space == KILLBLOCK):
		kill_player()



def direct_keypress(tap):

	global player, MOVES, board

	if (tap == curses.KEY_UP):
		direct_move('U')
	elif (tap == curses.KEY_LEFT):
		direct_move('L')
	elif (tap == curses.KEY_DOWN):
		direct_move('D')
	elif (tap == curses.KEY_RIGHT):
		direct_move('R')




######################################################################
########################-- question user about board-size --##########
######################################################################

def pause():

	global ttyRows, ttyCols, screen_cols, left_margin, top_margin

	play_audio('pause')

	pauseleft = (int(ttyCols/2) - 8) - left_margin
	pausetop = (int(ttyRows/2) - 4) - (int(board_rows / 4)) - top_margin
	print('\033[0m\033[40m')	

	print('\033[' + str(pausetop + top_margin) + ';' + str(pauseleft + left_margin) + 'H' + ' '*16)
	print('\033[' + str(pausetop + top_margin + 1) + ';' + str(pauseleft + left_margin) + 'H' + ' ' + chr(9556) + chr(9552)*12 + chr(9559) + ' ')
	print('\033[' + str(pausetop + top_margin + 2) + ';' + str(pauseleft + left_margin) + 'H' + ' ' + chr(9553) + '            ' + chr(9553) + ' ')
	print('\033[' + str(pausetop + top_margin + 3) + ';' + str(pauseleft + left_margin) + 'H' + ' ' + chr(9553) + '   PAUSED   ' + chr(9553) + ' ')
	print('\033[' + str(pausetop + top_margin + 4) + ';' + str(pauseleft + left_margin) + 'H' + ' ' + chr(9553) + '            ' + chr(9553) + ' ')
	print('\033[' + str(pausetop + top_margin + 5) + ';' + str(pauseleft + left_margin) + 'H' + ' ' + chr(9562) + chr(9552)*12 + chr(9565) + ' ')
	print('\033[' + str(pausetop + top_margin + 6) + ';' + str(pauseleft + left_margin) + 'H' + ' '*16)
	
	print('\033[H\033[0m')

	while(keypress == ord('p')):
		sleep(.08)

	play_audio('pause')

#####################################################################################################
#######################################################-- main function calls -######################
#####################################################################################################

system('reset')

plan_the_board()


def build_level():
	
	global board_rows, board_cols, reset_board, blank_board, board, beast_cnt, monster_cnt, egg_cnt, key_move, level, lives, score, points, BAKGRD, BLOCK, KILLBLOCK, countdown
	
	key_move = False
	block_type = BLOCK
	lvl_beast_cnt = 0
	lvl_monster_cnt = 0
	lvl_egg_cnt = 0
	
	print_board(board)
	sleep(1)	
	board = []
	board = build_the_board()
	print_board(board)
	sleep(1)

	if (lives == 0):
		if score > 0: score -= 50
		level = 1
		lives = 5
		points = 0
		lvl_beast_cnt = beast_cnt
		lvl_monster_cnt = monster_cnt
		lvl_egg_cnt = egg_cnt
		for i in range(1, len(player)): del player[1]
		for i in range(1, len(beasts)): del beasts[1]
		for i in range(1, len(monsters)): del monsters[1]
		for i in range(1, len(eggs)): del eggs[1]
	else:
		level += 1
		score += points
		points = 0
		for i in range(1, len(player)): del player[1]
		if (level < 9): lvl_beast_cnt = beast_cnt + level - 1
		if (level > 4): lvl_monster_cnt = level - 4
		if (level > 2): lvl_egg_cnt = level - 2
		if (level > 4): block_type = KILLBLOCK

	lower_boxes = int(play_rows * play_cols / 4 - 10)
	upper_boxes = int(play_rows * play_cols / 4 + 10)
	box_cnt = randint(lower_boxes, upper_boxes)
	
	box_step = 0
	block_step = 0	
	blockrow = 0
	blockcol = 0
	boxrow = 0
	boxcol = 0
	while(block_step < block_cnt):
		blockrow = randint(1, (board_rows - 1))
		blockcol = randint(1, (board_cols - 1))
		if(board[blockrow][blockcol] == BAKGRD):
			board[blockrow][blockcol] = block_type
		block_step += 1	

	while(box_step < box_cnt):
		boxrow = randint(1, (board_rows - 1))
		boxcol = randint(1, (board_cols - 1))
		if(board[boxrow][boxcol] == BAKGRD):
			board[boxrow][boxcol] = BOX
		box_step += 1	
	
	place_beasts(lvl_beast_cnt)
	place_monsters(lvl_monster_cnt)
	place_eggs(lvl_egg_cnt)
	place_player()
	
	countdown = 1
	key_move = True


####################################################################################################
#########################################################################-- take input func -- #####
####################################################################################################

def take_input():

	global debug, keypress, player, top_margin, left_margin, save_top, save_left, key_move
	
	stdscr = curses.initscr() 
	curses.cbreak()
	stdscr.keypad(1)
	stdscr.refresh()

	while(True):
		keypress = stdscr.getch()
		if keypress == ord('q'):
			system('clear')
			exit()
		elif keypress == ord('p'):
			keypress = stdscr.getch()
			keypress = ''
		elif keypress == ord('r'):
			plan_the_board()
			system('clear')
		elif keypress == ord('b'):
			if debug == True:
				debug = False
				top_margin = save_top
				left_margin = save_left
				system('clear')
			else:
				debug = True
				top_margin = 0
				left_margin = 0
				system('clear')
		if (key_move == True):
			if keypress == ord(' '):
				while (keypress == ord(' ')):
					keypress = stdscr.getch()
					player[1]['tug'] = not player[1]['tug']
					if (keypress != ord(' ')):
						tugspan = keypress # logs the present direction to compare for direction change
						while (tugspan == keypress): # this ensures the player has pull function until direction key changes.
							direct_keypress(keypress)
							player[1]['tug'] = True
							keypress = stdscr.getch()				
			if keypress != ord(' '):
				player[1]['tug'] = False
				direct_keypress(keypress)
	
#########################################################################################################
threading.Thread(target=take_input).start()  ###############-- the main game clock and print loop --#####
#########################################################################################################
countdown = 1

while(True):
	if keypress == ord('q'):
		system('reset')
		exit()
	elif keypress == ord('p'):
		pause()
	else:
		if ((lives == 0) | ((len(beasts) == 1) & (len(monsters) == 1) & (len(eggs) == 1))):
			if countdown == 0:
				if lives == 0: play_audio('loss')
				else: play_audio('win')
				system('echo \'pre-call\' >> level.txt')
				build_level()								
			countdown -= 1
		move_enemies(beasts)
		move_enemies(monsters)
		hatch_eggs()
		print_board(board)
		sleep(lcd_time)

################################################
input()
