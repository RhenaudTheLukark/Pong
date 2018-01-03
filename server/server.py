#!/usr/bin/python3
import socket
import select
import threading
import sys
import pygame
import random
import math
import time

sys.path.insert(0, "../client")
from pong_lib import *

server = socket.socket(socket.AF_INET6, socket.SOCK_STREAM, 0)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(('', 10000))
server.listen(1)
players = [] #Max 2

racket_coords = []
racket_dims = [20, 100]

ball = None

#Main function of the program
def main():
	global started
	started = False
	while True:
		if len(players) < 2:
			acceptPlayers()
		else:
			computeGame()

#Accept players when under 2 players
def acceptPlayers():
	read, w, ex = select.select([server]+players,[],[]) #Get all sockets with action
	for s in read:
		if s == server: #New connection
			print("Connection received")
			if len(players) >= 2: #Max 2 players
				print("Max connection number reached")
				s2, tmp = s.accept()
				s2.send("Max connection number reached")
				s2.close()
				continue
			s2, tmp = s.accept()
			s2.send("Welcome to the Pong server! Waiting for another player...\n")
			players.append(s2)
		else:
			print("Data received!")
			data = receive(s)

			# Receive no data = close connection
			if not data: 
				print("Connection closed")
				s.send(data)
				s.close()
				players.remove(s)
			else:
				s.send(data)

#Disconnect player if the connection has been closed
def detectDisconnect(player):
	player.close()
	players.remove(player)

def startGame():
	global width
	global height
	global racket_coords
	racket_coords = [[0, 0], [width - racket_dims[0], 0]]
	for s in players:
		s.send("Start|")
	throwBall()
	sendGameData()

def computeGame():
	global started
	if not started:
		print("Game start!")
		started = True
		startGame()
	
	# Receive data first
	read, w, ex = select.select(players, [], [])
	for s in read:
		data = receive(s)
		computeReceivedData(0 if s == players[0] else 1, data)

	#print("Data received!")
	
	# Compute ball
	ball.update()
	checkBallOnSide()
	
	# Then send data
	sendGameData()

	# Wait for next frame
	time.sleep(0.01)

def checkBallOnSide():
	playerId = 0 if ball.x - racket_dims[0] < 0 else 1 if ball.x + racket_dims[0] >= width else -1
	if playerId >= 0:
		if ball.y + ball.diam >= racket_coords[playerId][1] and ball.y <= racket_coords[playerId][1] + racket_dims[1]:
			if (playerId == 1 and (ball.direction < math.pi / 2 or ball.direction > 3 * math.pi / 2)) or (playerId == 0 and (ball.direction > math.pi / 2 and ball.direction < 3 * math.pi / 2)): 
				ball.direction = math.pi - ball.direction
				ball.speed = ball.speed + 0.2
		elif ball.x < 0 or ball.x >= width:
			print("Score for Player " + str(1 - playerId) + "!")
			throwBall()
	if ball.y < 0 or ball.y >= height - ball.diam:   # Stay in screen for Y axis
		ball.direction = -ball.direction
	setGoodBallDirection()
	
def setGoodBallDirection():
	while (ball.direction < 0):
		ball.direction = ball.direction + 2 * math.pi
	ball.direction = ball.direction % (2 * math.pi)

def computeReceivedData(s_index, data):
	# 0: Up Arrow
	# 1: Down Arrow
	global racket_coords
	data2 = data.split('|')[len(data.split('|')) - 2]
	inputs = data2.split('\n')
		
	if inputs[0] == "1" and inputs[1] == "0":
		racket_coords[s_index][1] = racket_coords[s_index][1] - 4
	elif inputs[0] == "0" and inputs[1] == "1":
		racket_coords[s_index][1] = racket_coords[s_index][1] + 4
	rectifyPosition(s_index)

def rectifyPosition(i):
	if racket_coords[i][0] < 0:
		racket_coords[i][0] = 0
	elif racket_coords[i][0] >= width - racket_dims[0]:
		racket_coords[i][0] = width - racket_dims[0]
	if racket_coords[i][1] < 0:
		racket_coords[i][1] = 0
	elif racket_coords[i][1] >= height - racket_dims[1]:
		racket_coords[i][1] = height - racket_dims[1]

def sendGameData():
	data = computeDataToSend()
	#print(str(data))
	#for i in range(len(data)):
	#	print("\nBegin data #" + str(i + 1) + ":\n" + data[i])
	
	for i in range(2):
		players[i].send(data[i] + "|")

	#print("Data sent!")

def computeDataToSend():
	# 0: Your player
	# 1: Other player
	# 2: Ball
	data = ["", ""]

	# Get players position
	for i in range(len(data)):
		for j in range(len(players)):
			for k in range(2): # Coordinates (x and y)
				currPlayerCoord = 1 - j if (i == 1 and k == 0) else j
				#print("i = " + str(i) + ", j = " + str(currPlayerCoord) + ", k = " + str(k) + ", data[i] = " + data[i] + ", gonna add " + str(racket_coords[currPlayerCoord][k]))
				data[i] = data[i] + str(racket_coords[currPlayerCoord][k]) + "\n"

	# Get ball position
	for i in range(len(data)):
		data[i] = data[i] + str(ball.x if i == 0 else width - ball.x) + "\n" + str(ball.y)

	return data

def throwBall():
	global ball
	ball = BallServer()

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
		while len(players) > 0:
			players[0].send("On a perdu un joueur!|")
			players[0].close()
			players.remove(players[0])
			server.close()
			sys.exit()
		return ""
	return data

main()
