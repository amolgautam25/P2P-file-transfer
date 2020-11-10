#!/usr/bin/env python3

import socket
import _thread
import pickle
import signal

HOST = '127.0.0.1'
PORT = 7734


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
    clientHostname=""
    while True:
        client_msg = conn_socket.recv(1024)
        if not client_msg:
            print("No messsage received!")
            break
        client_data = pickle.loads(client_msg)

        clientHostname = addr[0] + ":" + str(client_data[1])
        if clientHostname not in current_peers:
            current_peers[clientHostname] = client_data[1]
        #print(current_peers)

        print("CLIENT REQUEST:\n", client_data[0])

        if client_data[0] == 'EXIT':
            break
        else:
            #print("-------------",client_data)
            server_message_split = client_data[0].split('\r\n')
            if "ADD" in server_message_split[0]:
                if len(server_message_split) == 5 and "Host" in \
                        server_message_split[1] and "Port" in \
                        server_message_split[2] and "Title" in server_message_split[3]:
                    if 'P2P-CI/1.0' not in server_message_split[0]:
                        conn_socket.send(str.encode("505 P2P-CI Version Not Supported\r\n"))
                    else:
                        add_message_split = server_message_split[0].split()
                        host_message_split = server_message_split[1].split()
                        port_message_split = server_message_split[2].split()
                        title_message_split = server_message_split[3].split()

                        add_rfc_num = add_message_split[2]
                        add_rfc_title = ' '.join(title_message_split[1:])
                        cname = host_message_split[1] + ":" + port_message_split[1]

                        if add_rfc_num not in rfc_list:
                            rfc_list[add_rfc_num] = add_rfc_title
                            list_of_peers[add_rfc_num] = [cname]
                        else:
                            list_of_peers[add_rfc_num].append(cname)

                        msg = "P2P-CI/1.0 200 OK\r\n" + server_message_split[1] + "\r\n" + server_message_split[
                            2] + "\r\n" + \
                                  server_message_split[3] + "\r\n"
                        conn_socket.send(str.encode(msg))
                else:
                    conn_socket.send(str.encode("400 Bad Request\r\n"))

            elif "LIST" in server_message_split[0]:
                if len(server_message_split) == 4 and "Host" in server_message_split[1] and "Port" in \
                        server_message_split[2]:
                    list_message_split = server_message_split[0].split()

                    if 'P2P-CI/1.0' != list_message_split[2]:
                        conn_socket.send(str.encode("505 P2P-CI Version Not Supported\r\n"))
                    else:
                        if len(list_of_peers) == 0:
                            msg = "P2P-CI/1.0 404 Not Found\r\n"
                        else:
                            msg = "P2P-CI/1.0 200 OK\r\nFILE_TYPE RFC_NUM RFC_TITLE PEER PORT"
                            for rfc, value in list_of_peers.items():
                                for host in value:
                                    msg = msg + "\r\n" + "rfc " + str(rfc) + " " + str(rfc_list.get(rfc)) + " " + str(
                                        host.split(':')[0]) + " " + str(current_peers.get(host))
                            msg = msg + "\r\n"
                        conn_socket.send(str.encode(msg))
                else:
                    conn_socket.send(str.encode("400 Bad Request\r\n"))

            elif "LOOKUP" in server_message_split[0]:
                if len(server_message_split) == 5 and "Host" in server_message_split[1] and "Port" in \
                        server_message_split[2] and "Title" in server_message_split[3]:
                    lookup_message_split = server_message_split[0].split()
                    title_message_split = server_message_split[3].split()

                    if 'P2P-CI/1.0' != lookup_message_split[3]:
                        conn_socket.send(str.encode("505 P2P-CI Version Not Supported\r\n"))
                    else:
                        lookup_rfc_num = lookup_message_split[2]
                        rfc_title = ' '.join(title_message_split[1:])

                        if lookup_rfc_num in rfc_list and rfc_list[lookup_rfc_num] == rfc_title:
                            msg = "P2P-CI/1.0 200 OK"
                            r = list_of_peers.get(lookup_rfc_num)
                            for host in r:
                                msg = msg + "\r\n" + "RFC " + str(lookup_rfc_num) + " " + str(rfc_title) + " " + str(
                                    host.split(':')[0]) + " " + str(current_peers.get(host))
                            msg = msg + "\r\n"
                            conn_socket.send(str.encode(msg))
                        else:
                            conn_socket.send(str.encode("P2P-CI/1.0 404 Not Found\r\n"))
                else:
                    conn_socket.send(str.encode("400 Bad Request\r\n"))

    if clientHostname in current_peers:
        current_peers.pop(clientHostname, None)
    for rfc in list(list_of_peers):
        r = list_of_peers.get(rfc)
        if clientHostname in r:
            if len(r) != 1:
                r.remove(clientHostname)
                list_of_peers[rfc] = r
            else:
                rfc_list.pop(rfc, None)
                list_of_peers.pop(rfc, None)
    conn_socket.close()

def keyboardInterruptHandler(signal, frame):
    print("KeyboardInterrupt has been caught. Cleaning up!")
    ssocket.close()
    exit(0)


signal.signal(signal.SIGINT, keyboardInterruptHandler)

while 1:
    conn_socket, address = ssocket.accept()
    print("Client " + address[0] + " connected. \n")
    _thread.start_new_thread(connection_handler, (conn_socket, address))

