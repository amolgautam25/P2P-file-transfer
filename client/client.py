#!/usr/bin/env python3

import socket
import email.utils
import os
import pickle
import random
import time
import platform
import _thread
import sys
import signal

server_host = sys.argv[1]
server_port = int(sys.argv[2])

def peer_conn():
    pr_socket = socket.socket()
    pr_socket.bind(('0.0.0.0', c_port))
    pr_socket.listen(5)
    while True:
        peer_socket, peer_address = pr_socket.accept()
        peer_message = peer_socket.recv(1024)
        peer_message_split = peer_message.decode('utf-8').split("\r\n")
        if len(peer_message_split) == 4 and "GET RFC" in peer_message_split[0] and "Host" in peer_message_split[1] and "OS" in peer_message_split[
            2]:
            if 'P2P-CI/1.0' not in peer_message_split[0]:
                peer_socket.send(str.encode("505 P2P-CI Version Not Supported\r\n"))
            else:
                get_req = peer_message_split[0].split(" ")
                if get_req[0] == 'GET':
                    r_filepath = os.getcwd() + "/rfc/rfc" + str(get_req[2]) + ".txt"
                    rfc_file_data = open(r_filepath, 'r').read()
                    peer_reply = "P2P-CI/1.0 200 OK\r\n" \
                                    "Date: " + str(email.utils.formatdate(usegmt=True)) + "\r\n" \
                                                                                          "OS: " + str(
                        platform.platform()) + "\r\n" \
                                               "Last-Modified: " + str(
                        time.ctime(os.path.getmtime(r_filepath))) + "\r\n" \
                                                                       "Content-Length: " + str(len(rfc_file_data)) + "\r\n" \
                                                                                                             "Content-Type: text/plain\r\n"
                    print(peer_reply)
                    peer_reply = peer_reply + rfc_file_data
                    peer_socket.sendall(peer_reply.encode('utf-8'))
        else:
            peer_socket.send(str.encode("400 Bad Request\r\n"))

def peer_conn_thread(req_message, peer_host_name, peer_port_number, rfc_number):
    p_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    p_socket.connect((peer_host_name, int(peer_port_number)))
    print("\nPEER CONNECTION ESTABLISHED\n")
    p_socket.sendall(req_message.encode('utf-8'))

    get_reply_bytes = p_socket.recv(1024)
    pr = get_reply_bytes.decode('utf-8')
    prsplit = pr.split("\r\n")
    if 'P2P-CI/1.0 200 OK' in prsplit[0]:
        print('P2P-CI/1.0 200 OK')
        c_length = int(prsplit[4].split(" ")[1])
        pr = pr + p_socket.recv(c_length).decode('utf-8')
        peer_data = pr[12 + pr.find('text/plain\r\n') :]
        with open(os.getcwd() + "/rfc/rfc" + rfc_number + ".txt", 'w') as file:
            file.write(peer_data)
        print('File Received!')
    elif 'Version Not Supported' in prsplit[0] or 'Bad Request' in prsplit[0]:
        print(pr)
    p_socket.close()

def keyboardInterruptHandler(signal, frame):
    print("KeyboardInterrupt has been caught. Cleaning up!")
    c_Socket.close()
    exit(0)

signal.signal(signal.SIGINT, keyboardInterruptHandler)

c_Socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
c_Socket.connect((server_host, server_port))
print('Connected to server!')
c_hostname = c_Socket.getsockname()[0]
c_port = 60000 + random.randint(1, 5000)
#r = [c_port]
#cp = pickle.dumps(r)
#c_Socket.send(cp)
#c_Socket.close


#RFC_number:title
rfc_number_title_map={}
for f in os.listdir(os.getcwd()+"/rfc"):
    if 'rfc' in f:
        number=f[3:f.find(".")]
        rfc_number_title_map[number]=f.split('.')[0]
        req_message = "ADD RFC " + str(number) + " P2P-CI/1.0\r\n" \
                                                 "Host: " + str(c_hostname) + "\r\n" \
                                                                              "Port: " + str(c_port) + "\r\n" \
                                                                                                       "Title: " + str(
        rfc_number_title_map[number]) + "\r\n"
        print ("ADD REQUEST - TO THE SERVER:\n", req_message)
        c_Socket.send(pickle.dumps([req_message, c_port], -1))
        receivedData = c_Socket.recv(1024)
        print("RESPONSE TO ADD REQUEST:\n", receivedData.decode('utf-8'))
_thread.start_new_thread(peer_conn,())

while 1:
    user_input = input("Select one of the following : \n 1 ADD\n 2 GET\n 3 LIST\n 4 LOOKUP\n 5 EXIT\n")

    #ADD
    if user_input == "1":
        add_rfc_num = input("Input RFC number: ")
        add_rfc_title = input("Input RFC title: ")
        if os.path.isfile(os.getcwd() + "/rfc/rfc" + add_rfc_num + ".txt"):
            client_message_1 = "ADD RFC " + str(add_rfc_num) + " P2P-CI/1.0\r\n" \
                                                 "Host: " + str(c_hostname) + "\r\n" \
                                                                              "Port: " + str(c_port) + "\r\n" \
                                                                                                       "Title: " + str(
        add_rfc_title) + "\r\n"
            print("\nADD REQUEST - TO THE SERVER:\n", client_message_1)
            c_Socket.send(pickle.dumps([client_message_1, c_port], -1))
            receivedData = c_Socket.recv(1024)
            print("RESPONSE TO ADD REQUEST:\n", receivedData.decode('utf-8'))
        else:
            print("File not found!")

    #GET
    if user_input == "2":
        get_rfc_num = input("Input RFC number: ")
        get_rfc_title = input("Input RFC title: ")

        req_message = "LOOKUP RFC " + str(get_rfc_num) + " P2P-CI/1.0\r\n" \
                                                    "Host: " + str(c_hostname) + "\r\n" \
                                                                                 "Port: " + str(c_port) + "\r\n" \
                                                                                                          "Title: " + str(
        get_rfc_title) + "\r\n"
        print("\nLOOKUP REQUEST - TO THE SERVER:\n", req_message)
        c_Socket.sendall(pickle.dumps([req_message, c_port], -1))
        receivedData = c_Socket.recv(1024)
        response_received_string=receivedData.decode("utf-8")
        get_message_split = response_received_string.split('\r\n')
        print("RESPONSE TO LOOKUP REQUEST:\n")
        if '404 Not Found' in get_message_split[0] or 'Version Not Supported' in get_message_split[0] or 'Bad Request' in get_message_split[
            0]:
            print(receivedData.decode('utf-8'))
        else:
            print(receivedData.decode('utf-8'))
            get_message_split = get_message_split[1].split(" ")
            req_message  = "GET RFC " + str(get_rfc_num) + " P2P-CI/1.0\r\n" \
                                                 "Host: " + str(c_hostname) + "\r\n" \
                                                                              "OS: " + platform.platform() + "\r\n"
            print("GET REQUEST - TO THE PEER WITH RFC:\n", req_message)
            _thread.start_new_thread(peer_conn_thread, (req_message, get_message_split[3], get_message_split[4], get_rfc_num))

    #LIST
    if user_input == "3":
        client_message_1="LIST ALL P2P-CI/1.0\r\n" \
              "Host: " + str(c_hostname) + "\r\n" \
                                           "Port: " + str(c_port) + "\r\n"
        print("LIST REQUEST - TO THE SERVER\n", client_message_1)
        c_Socket.send(pickle.dumps([client_message_1, c_port], -1))
        receivedData = c_Socket.recv(1024)
        print("RESPONSE TO LIST REQUEST:\n", receivedData.decode('utf-8'))

    #lookup
    if user_input == "4":
        lookup_rfc_num = input("Input RFC number: ")
        lookup_rfc_title = input("Input RFC title: ")
        client_message_1 = req_message = "LOOKUP RFC " + str(lookup_rfc_num) + " P2P-CI/1.0\r\n" \
                                                    "Host: " + str(c_hostname) + "\r\n" \
                                                                                 "Port: " + str(c_port) + "\r\n" \
                                                                                                          "Title: " + str(
        lookup_rfc_title) + "\r\n"
        print("LOOKUP REQUEST:\n", client_message_1)
        c_Socket.send(pickle.dumps([client_message_1, c_port], -1))
        receivedData = c_Socket.recv(1024)
        print("RESPONSE TO LOOKUP RESPONSE:\n", receivedData.decode('utf-8'))

    #EXIT
    if user_input == "5":
        client_message_1 = "EXIT"
        c_Socket.send(pickle.dumps([client_message_1, c_port], -1))
        c_Socket.close()
        print("SHUTTING DOWN CLIENT")
        break
