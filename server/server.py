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
			s2.send("Welcome to the Pong server! Waiting for another player...")
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
	racket_coords = [[0, 0], [width - 37, 0]]
	for s in players:
		s.send("Start")
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
	
	# Then send data
	sendGameData()

	# Wait for next frame
	time.sleep(0.01)

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
	elif racket_coords[i][0] >= width - 37:
		racket_coords[i][0] = width - 37
	if racket_coords[i][1] < 0:
		racket_coords[i][1] = 0
	elif racket_coords[i][1] >= height - 100:
		racket_coords[i][1] = height - 100

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
	for i in range(2): # Data
		for j in range(2): # Player
			for k in range(2): # Coordinates (x and y)
				#print("i = " + str(i) + ", j = " + str(j) + ", k = " + str(k) + ", data[i] = " + data[i] + ", gonna add " + str(racket_coords[i == 1 and j or 1 - j][k]))
				data[i] = data[i] + str(racket_coords[j if i == 1 else 1 - j][k]) + "\n"

	# Get ball position
	for i in range(2):
		data[i] = data[i] + str(ball.x) + "\n" + str(ball.y)

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
	except(socket.error):
		print("Shoot, an exception has been caught while receiving the data.\nTime to drop a nuclear bomb on that connection!")
		s.close()
		players.remove(s)
		return ""
	return data

main()
