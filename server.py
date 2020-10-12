#!/usr/bin/env python3

import socket
import _thread

HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT = 7734        # Port to listen on (non-privileged ports are > 1023)

#Bind the port to the given port number
ssocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ssocket.bind((HOST,PORT))
ssocket.listen(5)

print ("Server is Up")

list_of_peers = {}      #A dictionary whose key is the RFC number and value is the list of peers using the RFC
rfc_list = {}			#A dictionary whose key is the RFC number and value is the title
current_peers = {} 		#A dictionary which contains active peers with the key representing the hostname and the value representing the port used for connecting to the server

def connection_handler (connectionsocket,addr):
    data=connectionsocket.recv(1024)
    print("The data sent was ( in bytes) "+ str(data))

while 1:
    connectionsocket, addr = ssocket.accept()
    _thread.start_new_thread(connection_handler, (connectionsocket, addr))
ssocket.close()
