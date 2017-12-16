#!/usr/bin/python3

import socket
import sys
from client_functions import *
from pong_lib import *

#server port
port = 10000
host = 0

ball = None
ball_coords = [0, 0]
rackets = [None, None]
racket_coords = [[0, 0], [0, 0]]

client_input = [False, False]

bg = (0x00, 0x00, 0x00)

def main():
    global host
    global port
    global client

    #verify the host was given
    try:
        host = sys.argv[1]
    except(IndexError):
        print("Entrez le nom d'un serveur pour vous connecter")
        return

    print("Connexion au serveur "+host+" en cours...\n")

    #Initialise the client
    client = socket.socket(socket.AF_INET6,socket.SOCK_STREAM)

    #Set the option of freeing the port as soon as possible on
    client.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)

    #Try to connect to the host
    try:
        client.connect((host,port))
    except(socket.error):
        print("Connexion echouee. Il doit etre deconnecte ou inexistant")
        return
    
    #Start the connection loop
    while True:
        #Receive a message from the server and print it
        mr = client.recv(4096)
        mr = mr.decode()
        print(mr + "\n")
        if(mr.strip() == "Max connection number reached"):
            break
        if(mr.find("Start") > -1):
            play(client)
        #Wait for an input
        #ms = raw_input("> ")

        #Send the input
        #ms = ms.encode()
        #client.send(ms)


    #Stop the client
    client.close()

#Initialise Pygame
def init():
    global width
    global height
    global screen
    pygame.init()
    screen = pygame.display.set_mode((width, height))

#Play an online game of Pong
def play(s):
    print("Game starts")
    init()

    global ball
    global rackets	
    ball = pygame.image.load("../resource/image/ball_new.png")
    rackets = [None,None]
    for i in range(2):
        rackets[i] = pygame.image.load("../resource/image/racket_new.png")

    while True:
        for e in pygame.event.get():
            # Check for exit
            if e.type == pygame.QUIT:
                sys.exit()

            # Check for racket movements
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_UP:
                    #update upTrue
                    client_input[0] = True
                if e.key == pygame.K_DOWN:
                    #update downTrue
                    client_input[1] = True
            elif e.type == pygame.KEYUP:
                if e.key == pygame.K_UP:
                    #update upFalse
                    client_input[0] = False
                if e.key == pygame.K_DOWN:
                    #update downFalse
                    client_input[1] = False
        sendData()
        receiveData()
    	# Display everything
    	screen.fill(bg)
        screen.blit(ball, ball_coords)
        for i in range(2):
            screen.blit(rackets[i], racket_coords[i])
        pygame.display.flip()

        # sleep 10ms, since there is no need for more than 100Hz refresh :)
	# but the refresh is handled by the server now
        #pygame.time.delay(10)

def sendData():
	data = ""
	for i in range(len(client_input)):
		data = data + ("1" if client_input[i] else "0") + ("\n" if i != len(client_input) - 1 else "")
	client.send(data + "|")

def receiveData():
	data = client.recv(4096)
	data2 = data.split('|')[len(data.split('|')) - 2]
	coords = data2.split('\n')

	# Test data sent
	#testData = "["
	#for i in range(len(coords)):
	#	testData = testData + coords[i] + ("," if i < len(coords) - 1 else "]")
	#print("testData = " + testData)

	for i in range(len(coords)):
		if i < 4:
			racket_coords[int(math.floor(i/2))][i % 2] = getNum(coords[i])
		else: 
			ball_coords[i % 2] = getNum(coords[i])

###########
# Utility #
###########

def getNum(string):
	if string.find(".") > -1:
		return float(string)
	else:
		return int(string)

main()
