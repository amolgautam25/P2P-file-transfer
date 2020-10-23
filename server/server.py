#!/usr/bin/env python3

import socket
import _thread

HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT = 7734  # Port to listen on (non-privileged ports are > 1023)

# Bind the port to the given port number
ssocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ssocket.bind((HOST, PORT))
ssocket.listen(5)

print("Server is Up")

list_of_peers = {}
rfc_list = {}
current_peers = {}


def connection_handler(connectionsocket, addr):
    while 1:
        data = connectionsocket.recv(1024)
        print("The data sent was ( in bytes) " + str(data))
        #process the data

        #if the client needs to send more data .

        if not data:
            break


while 1:
    connectionsocket, addr = ssocket.accept()
    _thread.start_new_thread(connection_handler, (connectionsocket, addr))
ssocket.close()
