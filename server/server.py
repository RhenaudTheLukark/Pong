#!/usr/bin/python3
import socket
import select
import threading
server = socket.socket(socket.AF_INET6, socket.SOCK_STREAM, 0)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(('', 10000))
server.listen(1)
players = [] #Max 2

def main():
	while True:
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
				s2.send("Welcome to the Pong server! (NB: This is a ping server for now)")
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

main()