#!/usr/bin/env python3

import socket

HOST = '127.0.0.1'  # The server's hostname or IP address
PORT = 7734        # The port used by the server

val=input("Enter a message that you would like to send")

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    encoded_bytes=val.encode('utf-8')
    s.sendall(encoded_bytes)
    #data = s.recv(1024)

#print('Received', repr(data))