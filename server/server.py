#!/usr/bin/env python3

import socket
import _thread
import pickle

HOST = '127.0.0.1'
PORT = 7734

global list_of_peers, rfc_list, current_peers
ssocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ssocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
ssocket.bind(('', PORT))
ssocket.listen(5)

print("Server is Up!\n")

# number:[hostname]
list_of_peers = {}

# a list containing the RFC indexes available at each peer - number:title
rfc_list = {}

# a list with information about the currently active peers - hostname:port
current_peers = {}


def connection_handler(conn_socket, addr):
    ports_list = pickle.loads(conn_socket.recv(1024))
    clientHostname = addr[0] + ":" + str(ports_list[0])
    current_peers[clientHostname] = ports_list[0]
    while 1:
        message_received = conn_socket.recv(1024)
        if not message_received:
            print("No messsage received!")
            break
        message_list = pickle.loads(message_received)
        #print(message_list)
        print("CLIENT REQUEST:\n", message_list[0])

        if message_list[0][0] == 'E':
            break
        else:
            server_message_split = message_list[0].split('\r\n')
            if "ADD" in server_message_split[0]:
                if len(server_message_split) == 5 and "Host" in \
                        server_message_split[1] and "Port" in \
                        server_message_split[2] and "Title" in server_message_split[3]:
                    if 'P2P-CI/1.0' not in server_message_split[0]:
                        message = "505 P2P-CI Version Not Supported\r\n"
                        conn_socket.send(message)
                    else:
                        add_message_split = server_message_split[0].split()
                        host_message_split = server_message_split[1].split()
                        port_message_split = server_message_split[2].split()
                        title_message_split = server_message_split[3].split()

                        rfc_number = add_message_split[2]
                        client_host_name = host_message_split[1]
                        client_port_number = port_message_split[1]
                        rfc_title = ' '.join(title_message_split[1:])
                        p2p_version = add_message_split[3]
                        cname = client_host_name + ":" + client_port_number

                        if rfc_number not in rfc_list:
                            rfc_list[rfc_number] = rfc_title
                            list_of_peers[rfc_number] = [cname]
                        else:
                            rfc_host_list = list_of_peers.get(rfc_number)
                            rfc_host_list.append(cname)
                            list_of_peers[rfc_number] = rfc_host_list

                        message = "P2P-CI/1.0 200 OK\r\n" + server_message_split[1] + "\r\n" + server_message_split[
                            2] + "\r\n" + \
                                  server_message_split[3] + "\r\n"
                        conn_socket.send(str.encode(message))


                else:
                    message = "400 Bad Request\r\n"
                    conn_socket.send(message)
            elif "LIST" in server_message_split[0]:
                if len(server_message_split) == 4 and "Host" in server_message_split[1] and "Port" in \
                        server_message_split[2]:
                    list_message_split = server_message_split[0].split()
                    host_message_split = server_message_split[1].split()
                    port_message_split = server_message_split[2].split()

                    if 'P2P-CI/1.0' != list_message_split[2]:
                        message = "505 P2P-CI Version Not Supported\r\n"
                        message_bytes = bytes(message, 'utf-8')
                        conn_socket.send(message_bytes)
                    else:
                        client_host_name = host_message_split[1]
                        client_port_number = port_message_split[1]
                        if len(list_of_peers) == 0:
                            message = "P2P-CI/1.0 404 Not Found\r\n"
                        else:
                            message = "P2P-CI/1.0 200 OK"
                            for rfc, value in list_of_peers.items():
                                rfc_host_list = list_of_peers[rfc]
                                for host in rfc_host_list:
                                    temp = "rfc " + str(rfc) + " " + str(rfc_list.get(rfc)) + " " + str(
                                        host[:host.find(":")]) + " " + str(current_peers.get(host))
                                    message = message + "\r\n" + temp
                            message = message + "\r\n"
                        message_bytes = bytes(message, 'utf-8')
                        conn_socket.send(message_bytes)
                else:
                    message = "400 Bad Request\r\n"
                    message_bytes = bytes(message, 'utf-8')
                    conn_socket.send(message_bytes)
            elif "LOOKUP" in server_message_split[0]:
                if len(server_message_split) == 5 and "Host" in server_message_split[1] and "Port" in \
                        server_message_split[2] and "Title" in server_message_split[3]:
                    lookup_message_split = server_message_split[0].split()
                    host_message_split = server_message_split[1].split()
                    port_message_split = server_message_split[2].split()
                    title_message_split = server_message_split[3].split()

                    if 'P2P-CI/1.0' != lookup_message_split[3]:
                        message = "505 P2P-CI Version Not Supported\r\n"
                        message_bytes = bytes(message, 'utf-8')
                        conn_socket.send(message_bytes)
                    else:
                        rfc_number = lookup_message_split[2]
                        client_host_name = host_message_split[1]
                        client_port_number = port_message_split[1]
                        rfc_title = ' '.join(title_message_split[1:])
                        if rfc_number in rfc_list and rfc_list[rfc_number] == rfc_title:
                            message = "P2P-CI/1.0 200 OK"
                            rfc_host_list = list_of_peers.get(rfc_number)
                            for host in rfc_host_list:
                                temp = "RFC " + str(rfc_number) + " " + str(rfc_title) + " " + str(
                                    host[:host.find(":")]) + " " + str(current_peers.get(host))

                                message = message + "\r\n" + temp
                            message = message + "\r\n"
                            message_bytes = bytes(message, 'utf-8')
                            conn_socket.send(message_bytes)
                        else:
                            message = "P2P-CI/1.0 404 Not Found\r\n"
                            message_bytes = bytes(message, 'utf-8')
                            conn_socket.send(message_bytes)


                else:
                    message = "400 Bad Request\r\n"
                    message_bytes = bytes(message, 'utf-8')
                    conn_socket.send(message_bytes)
    if clientHostname in current_peers:
        current_peers.pop(clientHostname, None)
    for rfc in list(list_of_peers):
        rfc_host_list = list_of_peers.get(rfc)
        if clientHostname in rfc_host_list:
            if len(rfc_host_list) == 1:
                rfc_list.pop(rfc, None)
                list_of_peers.pop(rfc, None)
            else:
                rfc_host_list.remove(clientHostname)
                list_of_peers[rfc] = rfc_host_list
    conn_socket.close()

while 1:
    conn_socket, addr = ssocket.accept()
    print("Client " + addr[0] + " connected. \n")
    _thread.start_new_thread(connection_handler, (conn_socket, addr))
ssocket.close()
