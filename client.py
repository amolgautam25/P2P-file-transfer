#!/usr/bin/env python3

import socket
import platform

HOST = '127.0.0.1'  # The server's hostname or IP address
PORT = 7734  # The port used by the server

c_Socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
c_Socket.connect((HOST, PORT))
print('connected to server')
c_hostname = c_Socket.getsockname()
c_port = 60001


def add_request(client_rfc_num, client_rfc_title):
    message = "ADD RFC " + str(client_rfc_num) + " P2P-CI/1.0\r\n" \
                                                 "Host: " + str(c_hostname) + "\r\n" \
                                                                              "Port: " + str(c_port) + "\r\n" \
                                                                                                       "Title: " + str(
        client_rfc_title) + "\r\n"
    return message


# Create the LOOKUP Request message
def lookup_request(client_rfc_num, client_rfc_title):
    message = "LOOKUP RFC " + str(client_rfc_num) + " P2P-CI/1.0\r\n" \
                                                    "Host: " + str(c_hostname) + "\r\n" \
                                                                                 "Port: " + str(c_port) + "\r\n" \
                                                                                                          "Title: " + str(
        client_rfc_title) + "\r\n"
    return message


# Create the GET Request message
def get_request(client_rfc_num):
    message = "GET RFC " + str(client_rfc_num) + " P2P-CI/1.0\r\n" \
                                                 "Host: " + str(c_hostname) + "\r\n" \
                                                                              "OS: " + platform.platform() + "\r\n"
    return message


# Create the LIST Request message
def list_request():
    message = "LIST ALL P2P-CI/1.0\r\n" \
              "Host: " + str(c_hostname) + "\r\n" \
                                           "Port: " + str(c_port) + "\r\n"
    return message


while 1:
    user_input = input("Select one of the following : 1 ADD\n 2 GET\n 3 LIST\n 4 LOOKUP\n 5 EXIT\n")

    #ADD
    if user_input == "1":
        # form a request to be sent to the server
        rfc_num=input("Enter RFC number")
        rfc_title=input("Enter RFC title")
        client_message_1=add_request(rfc_num, rfc_title)
        print(client_message_1)
        encoded_bytes = client_message_1.encode('utf-8')
        c_Socket.sendall(encoded_bytes)
        # receive a response back
        # send the file to the server ( correct me if i am wrong )
        pass

    #GET
    if user_input == "2":
        # form a request to be sent to the server
        client_rfc_num=input("Enter client RFC number")
        client_message_1=get_request(client_rfc_num)
        print(client_rfc_num)
        encoded_bytes = client_message_1.encode('utf-8')
        c_Socket.sendall(encoded_bytes)
        pass

    #LIST
    if user_input == "3":
        client_message_1=list_request()
        print(client_message_1)
        # form a request to be sent to the server
        encoded_bytes = client_message_1.encode('utf-8')
        c_Socket.sendall(encoded_bytes)
        pass

    #lookup
    if user_input == "4":
        rfc_num = input("Enter RFC number")
        rfc_title = input("Enter RFC title")
        client_message_1 = lookup_request(rfc_num, rfc_title)
        print(client_message_1)
        # form a request to be sent to the server
        encoded_bytes = client_message_1.encode('utf-8')
        c_Socket.sendall(encoded_bytes)
        pass

    #EXIT
    if user_input == "5":
        # just exit the program
        print("Shutting down client")
        break
