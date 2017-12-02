#!/usr/bin/python3

import socket
import sys
import client_functions

#server port
port = 10000
host = 0

def main():

    global host
    global port

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
        print(mr)
        if(mr.strip() == "Max connection number reached"):
            break
        if(mr.strip() == "Start")
            play(client)
        #Wait for an input
        #ms = raw_input("> ")

        #Send the input
        #ms = ms.encode()
        #client.send(ms)


    #Stop the client
    client.close()

main()
