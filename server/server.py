#!/usr/bin/python3
import socket
import select
import threading
import sys
import pygame
import random
import math
import time

from pong_lib import *

server = socket.socket(socket.AF_INET6, socket.SOCK_STREAM, 0)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(('', 10000))
server.listen(1)
players = [] #Max 2
score = [0, 0]
effect = [0, 0]
effect_timer = [0, 0]

racket_coords = []
racket_dims = [20, 100]
racket_dims_effect = [125, 80]

ball = None

item = []
item_timer = float(random.randrange(5, 10)) / 50
last_clock = 0

# Main function of the program
def main():
	global started
	started = False
	while True:
		if len(players) < 2:
			acceptPlayers()
		else:
			computeGame()

# Accept players when under 2 players
def acceptPlayers():
	read, w, ex = select.select([server]+players,[],[]) # Get all sockets with action
	for s in read:
		if s == server: # New connection
			print("Connection received")
			if len(players) >= 2: # Max 2 players
				print("Max connection number reached")
				s2, tmp = s.accept()
				send(s2, "Max connection number reached")
				s2.close()
				continue
			s2, tmp = s.accept()
			send(s2, "Welcome to the Pong server! Waiting for another player...\n")
			players.append(s2)
		else:
			print("Data received!")
			data = receive(s)

			# Receive no data = close connection
			if not data: 
				print("Connection closed")
				send(s, data)
				s.close()
				players.remove(s)
			else:
				s.send(data)

# Init values needed for the game to be launched
def startGame():
	global width
	global racket_coords
	global score

	racket_coords = [[0, 0], [width - racket_dims[0], 0]]
	score = [0, 0]
    # Needed for the clients to start the game
	for s in players:
		send(s, "Start|")
	throwBall()
    # Send data with no data type
	sendGameData("")

# Game routine
def computeGame():
	global started
    # First frame of the game: init values needed with startGame()
	if not started:
		print("Game start!")
		started = True
		startGame()
	
	# Receive data first
	read, w, ex = select.select(players, [], [])
	for s in read:
		data = receive(s)
		computeReceivedData(0 if s == players[0] else 1, data)
	
	# Compute ball
	ball.update()
	checkBallOnSide()

	# Items	
	global item
	index_item = 0
	while index_item < len(item):
	        item[index_item].update()
		if not checkItemOnSide(item[index_item], index_item):
			index_item = index_item + 1

	# Item spawning
	global last_clock
	global item_timer
	curr_time = time.clock()
	item_timer = item_timer if last_clock == 0 else item_timer - (curr_time - last_clock)
	if item_timer <= 0: 
		throwItem()
		item_timer = float(random.randrange(5, 10)) / 50

	# Item check timer
	global effect_timer
	global effect
	for i in range(len(effect_timer)):
		if effect_timer[i] > 0:
			effect_timer[i] = effect_timer[i] if last_clock == 0 else effect_timer[i] - (curr_time - last_clock)
			if effect_timer[i] <= 0:
				effect[i] = 0
				sendGameData("I")

    # Store last time for time difference between this frame and the next
	last_clock = curr_time
	
	# Then send position data
	sendGameData("P")

	# Wait for next frame
	time.sleep(0.01)

# Mirrors the ball if it hits a racket, gives a point and throw the ball again if it reached a side.
def checkBallOnSide():
	# Stores player ID who handles the ball 
	playerId = 0 if ball.x - racket_dims[0] < 0 else 1 if ball.x + ball.diam + racket_dims[0] >= width else -1
	if playerId >= 0:
		# If collision with player, mirror the ball's direction to the other side
		racket_height = (racket_dims[1] if (effect[playerId] > 2 or effect[playerId] == 0) else racket_dims_effect[effect[playerId] - 1])
		if ball.y + ball.diam >= racket_coords[playerId][1] and ball.y <= racket_coords[playerId][1] + racket_height:
			if (playerId == 1 and (ball.direction < math.pi / 2 or ball.direction > 3 * math.pi / 2)) or (playerId == 0 and (ball.direction > math.pi / 2 and ball.direction < 3 * math.pi / 2)): 
				ball.direction = math.pi - ball.direction
				ball.speed = ball.speed + 0.2
        	# If the ball reaches the border, it increases the other player's score
		elif ball.x < 0 or ball.x + ball.diam >= width:
			print("Score for Player " + str(1 - playerId + 1) + "!")
			score[1 - playerId] = score[1 - playerId] + 1
			if score[1 - playerId] == 5:
				sendGameData("F", ["The game is set! You win!", "The game is set! You lost!"])
				closeGame()
			else:
				sendGameData("S")
				throwBall()
	# Stay in screen for Y axis
	if ball.y < 0 or ball.y >= height - ball.diam:
		ball.direction = -ball.direction
	setGoodBallDirection()

# Applies the bonus if it hits a racket, deletes it if it goes out of the screen completely.
def checkItemOnSide(localItem, index):
	global item
	playerId = 0 if localItem.x - racket_dims[0] < 0 else 1 if localItem.x + racket_dims[0] + localItem.dim >= width else -1
	if playerId >= 0:
        # If collision with player, applies the effect
		if localItem.y + localItem.dim >= racket_coords[playerId][1] and localItem.y <= racket_coords[playerId][1] + racket_dims[1]:
			effect[playerId] = localItem.type
			effect_timer[playerId] = 0.1
			sendGameData("I")
			item.remove(item[index])
			return True
        	# If the item reaches the border, it is destroyed
        	elif localItem.x < -localItem.dim or localItem.x >= width:
			item.remove(item[index])
			return True
	return False

# Resets the ball's direction between 0 and 2pi.
def setGoodBallDirection():
	while (ball.direction < 0):
		ball.direction = ball.direction + 2 * math.pi
	ball.direction = ball.direction % (2 * math.pi)

# Computes the data received by a given socket.
def computeReceivedData(s_index, data):
	# 0: Up Arrow
	# 1: Down Arrow
	global racket_coords
	data2 = data.split('|')[len(data.split('|')) - 2]
	inputs = data2.split('\n')
		
	# Manage inputs and the rackets' position
	if inputs[0] == "1" and inputs[1] == "0":
		racket_coords[s_index][1] = racket_coords[s_index][1] - (4 if effect[s_index] < 3 else (5 if effect[s_index] == 3 else (-4 if effect[s_index] == 5 else 3)))
	elif inputs[0] == "0" and inputs[1] == "1":
		racket_coords[s_index][1] = racket_coords[s_index][1] + (4 if effect[s_index] < 3 else (5 if effect[s_index] == 3 else (-4 if effect[s_index] == 5 else 3)))
	rectifyPosition(s_index)

# Rectify a racket's position to make so it stays on screen totally.
def rectifyPosition(i):
	if racket_coords[i][0] < 0:
		racket_coords[i][0] = 0
	elif racket_coords[i][0] >= width - racket_dims[0]:
		racket_coords[i][0] = width - racket_dims[0]
	if racket_coords[i][1] < 0:
		racket_coords[i][1] = 0
	elif racket_coords[i][1] >= height - (racket_dims[1] if (effect[i] > 2 or effect[i] == 0) else racket_dims_effect[effect[i] - 1]):
		racket_coords[i][1] = height - (racket_dims[1] if (effect[i] > 2 or effect[i] == 0) else racket_dims_effect[effect[i] - 1])

# Sends data to the players.
def sendGameData(dataType, dataText = None):
	data = computeDataToSend(dataType, dataText)

	#if dataType == "P":
	#	print(str(data))
	#	for i in range(len(data)):
	#		print("\nBegin data #" + str(i + 1) + ":\n" + data[i])
	
	for i in range(2):
		send(players[i], data[i] + "|")

# Compute the data to send to the players.
def computeDataToSend(dataType, dataText):
	# Type P:
	# 	0: Your player
	# 	1: Other player
	# 	2: Ball

	# Type S:
	# 	0: Score self
	#	1: Score other

	# Type F:
	#	0: Text to display

	# Type I:
	#	0: Effet joueur 1
	#	1: Effet joueur 2
	data = [dataType + "\n", dataType + "\n"]

	for i in range(len(data)):
		if dataType == "F":
			data[i] = data[i] + dataText[i if score[0] == 5 else 1 - i]
		elif dataType == "I":
			data[i] = data[i] + str(effect[i if i == 0 else 1 - i]) + "\n" + str(effect[1 - i if i == 0 else i])
		else:
			for j in range(len(players)):
				if dataType == "S":
					currPlayer = 1 - j if i == 1 else j
					data[i] = data[i] + str(score[currPlayer]) + ("\n" if j == 0 else "")
				elif dataType == "P":
					for k in range(2): # Coordinates (x and y)
						currPlayer = 1 - j if (i == 1 and k == 0) else j
						data[i] = data[i] + str(racket_coords[currPlayer][k]) + "\n"

	if dataType == "P":
		for i in range(len(data)):
			# Get ball position
			data[i] = data[i] + str(ball.x if i == 0 else width - ball.x - ball.diam) + "\n" + str(ball.y) + "\n"
			# Effects
			data[i] = data[i] + str(effect[i if i == 0 else 1 - i]) + "\n" + str(effect[1 - i if i == 0 else i])
			# Items
			for j in range(len(item)):
				data[i] = data[i] + "\n" + str(item[j].id) + "\n" + str(item[j].type) + "\n" + str(item[j].x if i == 0 else width - item[j].x - item[j].dim) + "\n" + str(item[j].y)
					
	return data

# Puts the ball back at the centerand throws it again in the game.
def throwBall():
	global ball
	ball = BallServer()

# Spawns an item in game.
def throwItem():
        global item
	item.append(ItemServer(0 if len(item) == 0 else item[0].id + 1))


###########
# Utility #
###########

def receive(s):
	try:
		data = s.recv(4096)
	except socket.error as err:
		errno, string = err
		print("Shoot, an exception has been caught while receiving the data.\nTime to drop a nuclear bomb on that connection!\n")
		print(string)
		s.close()
		players.remove(s)
		closeGame("On a perdu un joueur!")
		return ""
	return data

def send(s, data):
	try:
		s.send(data)
	except socket.error as err:
		errno, string = err
		print("Shoot, an exception has been caught while receiving the data.\nTime to drop a nuclear bomb on that connection!\n")
		print(string)
		s.close()
		players.remove(s)
		closeGame("On a perdu un joueur!")

def closeGame(endMess = None):
	while len(players) > 0:
		if endMess != None:
			players[0].send("E\n" + endMess + "|")
		players[0].close()
		players.remove(players[0])
	server.close()
	sys.exit()

main()
