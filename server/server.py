#!/usr/bin/python3
import socket
import select
import threading
import sys
import pygame
import random
import math

server = socket.socket(socket.AF_INET6, socket.SOCK_STREAM, 0)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(('', 10000))
server.listen(1)
players = [] #Max 2

started = False
ball = []
width = 800 #temp
height = 600 #temp

#Main function of the program
def main():
	if len(players) < 2:
		acceptPlayers()
	else
		computeGame()

#Accept players when under 2 players
def acceptPlayers():
	read, w, ex = select.select([server]+players,[],[]) #Get all sockets with action
	for s in read:
		if s == server: #New connection
			print("Connexion received")
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
			data = s.recv(4096)
			if not data: 
				print("Connexion closed")
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
	for s in players:
		s.send("Start")
	throwBall()

def computeGame():
	if not started:
		started = True
		startGame()

def computeReceivedData(data):
	print("I live!")

def sendGameData():
	print("I live!")

def throwBall():
	ball = Ball()

main()