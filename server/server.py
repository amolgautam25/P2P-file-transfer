#!/usr/bin/env python3

import socket
import _thread
import pickle

HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT = 7734  # Port to listen on (non-privileged ports are > 1023)

# Bind the port to the given port number
ssocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ssocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
ssocket.bind((HOST, PORT))
ssocket.listen(5)

print("Server is Up")

list_of_peers = {}
rfc_list = {}
current_peers = {}


def connection_handler(connectionsocket, addr):
        initial_data = pickle.loads(connectionsocket.recv(1024))
        host_name = addr[0] + ":" + str(initial_data[0])
        # Insert the information into data structures
        current_peers[host_name]= initial_data[0]
        # Request received from client for a service
        while 1:
            message_received = connectionsocket.recv(1024)
            if not message_received:
                break
            message_list = pickle.loads(message_received)
            print("Request received from the client")
            print(message_list[0])
            # EXIT Request
            if message_list[0][0] == 'E':
                break
            # ADD Request
            elif message_list[0][0] == 'A':
                print("A started --------")
                split_data = message_list[0].split('\r\n')
                # Check for BAD REQUEST case
                if len(split_data) == 5 and "ADD RFC " in split_data[0] and "Host: " in split_data[1] and "Port: " in \
                    split_data[2] and "Title: " in split_data[3]:
                    # Check for VERSION NOT SUPPORTED case
                    # If proper then add the data from the request and echo back the same request with OK Response
                    if 'P2P-CI/1.0' in split_data[0]:
                        # Retrieve the newly added RFC file information from request
                        rfc_number = split_data[0][split_data[0].find("C ") + 2:split_data[0].find(" P")]
                        client_host_name = split_data[1][split_data[1].find("Host: ") + 6:]
                        client_port_number = split_data[2][split_data[2].find("Port: ") + 6:]
                        rfc_title = split_data[3][split_data[3].find("Title: ") + 7:]
                        p2p_version = split_data[0][split_data[0].find(" P") + 1:]

                        # Add the RFC file information into the data structures
                        if rfc_number not in rfc_list:
                            rfc_list[rfc_number]= rfc_title
                            list_of_peers[rfc_number]=[client_host_name]
                        else:
                            rfc_host_list=list_of_peers[rfc_number]
                            rfc_host_list.append(client_host_name)
                            list_of_peers[rfc_number]=rfc_host_list

                        # Echo back the request with OK response to the client
                        message = "P2P-CI/1.0 200 OK\r\n" + split_data[1] + "\r\n" + split_data[2] + "\r\n" + \
                                      split_data[3] + "\r\n"
                        connectionsocket.send(str.encode(message))
                        print("A sends------")
                    else:
                        message = "505 P2P-CI Version Not Supported\r\n"
                        connectionsocket.send(message)
                else:
                    message = "400 Bad Request\r\n"
                    connectionsocket.send(message)
            elif message_list[0][0]=="L" and message_list[0][1]=="I":
                split_data = message_list[0].split('\r\n')
                # Check for BAD REQUEST case
                if len(split_data) == 4 and "LIST ALL " in split_data[0] and "Host: " in split_data[1] and "Port: " in \
                        split_data[2]:
                    p2p_version = split_data[0][split_data[0].find(" P") + 1:]
                    # Check for VERSION NOT SUPPORTED case
                    # If proper then reply with the list of RFC and their peer information
                    if p2p_version == 'P2P-CI/1.0':
                        # Retrieve information from request
                        client_host_name = split_data[1][split_data[1].find("Host: ") + 6:]
                        client_port_number = split_data[2][split_data[2].find("Port: ") + 6:]
                        # Reply to the request by sending the response to client
                        message=""
                        if len(list_of_peers)==0:
                            message = "P2P-CI/1.0 404 Not Found\r\n"
                        else:
                            message = "P2P-CI/1.0 200 OK"
                            print ("LIST OF PEERS ---- " ,list_of_peers)
                            print ("Current peers -----",current_peers)
                            for rfc,value in list_of_peers.items():
                                rfc_host_list = list_of_peers[rfc]
                                print("RFC HOST LIST " ,rfc_host_list)
                                for host in rfc_host_list:
                                    temp = "rfc " + str(rfc) + " " + str(rfc_list.get(rfc)) + " " + str(
                                        value) + " " + str(current_peers.get(host))
                                    message = message + "\r\n" + temp
                            message = message + "\r\n"
                        message_bytes=bytes(message,'utf-8')
                        connectionsocket.send(message_bytes)
                    else:
                        message = "505 P2P-CI Version Not Supported\r\n"
                        message_bytes = bytes(message, 'utf-8')
                        connectionsocket.send(message_bytes)
                else:
                    message = "400 Bad Request\r\n"
                    message_bytes = bytes(message, 'utf-8')
                    connectionsocket.send(message_bytes)
            elif message_list[0][0]=="L" and message_list[0][1]=="O":
                split_data = message_list[0].split('\r\n')
                # Check for BAD REQUEST case
                if len(split_data) == 5 and "LOOKUP RFC " in split_data[0] and "Host: " in split_data[1] and "Port: " in \
                        split_data[2] and "Title: " in split_data[3]:
                    p2p_version = split_data[0][split_data[0].find(" P") + 1:]
                    # Check for VERSION NOT SUPPORTED case
                    # If proper then reply with the requested RFC file information
                    if p2p_version == 'P2P-CI/1.0':
                        # Retrieve requested RFC file information from request
                        rfc_number = split_data[0][split_data[0].find("C ") + 2:split_data[0].find(" P")]
                        client_host_name = split_data[1][split_data[1].find("Host: ") + 6:]
                        client_port_number = split_data[2][split_data[2].find("Port: ") + 6:]
                        rfc_title = split_data[3][split_data[3].find("Title: ") + 7:]
                        # Reply to the request by sending the RFC file information response to client
                        if rfc_number in rfc_list and rfc_list[rfc_number] == rfc_title:
                            message = "P2P-CI/1.0 200 OK"
                            rfc_host_list = list_of_peers.get(rfc_number)
                            for host in rfc_host_list:
                                temp = "RFC " + str(rfc_number) + " " + str(rfc_title) + " " + str(host) + " " + str(
                                    current_peers.get(host))
                                message = message + "\r\n" + temp
                            message = message + "\r\n"
                            message_bytes = bytes(message, 'utf-8')
                            connectionsocket.send(message_bytes)
                        else:
                            message = "P2P-CI/1.0 404 Not Found\r\n"
                            message_bytes = bytes(message, 'utf-8')
                            connectionsocket.send(message_bytes)
                    else:
                        message = "505 P2P-CI Version Not Supported\r\n"
                        message_bytes = bytes(message, 'utf-8')
                        connectionsocket.send(message_bytes)
                else:
                    message = "400 Bad Request\r\n"
                    message_bytes = bytes(message, 'utf-8')
                    connectionsocket.send(message_bytes)
        connectionsocket.close()


while 1:
    connectionsocket, addr = ssocket.accept()
    _thread.start_new_thread(connection_handler, (connectionsocket, addr))
ssocket.close()
