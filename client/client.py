#!/usr/bin/env python3

import socket
import email
import os
import pickle
import random
import time
import platform

HOST = '127.0.0.1'  # The server's hostname or IP address
PORT = 7734  # The port used by the server

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


def upload_thread():
    # Create a upload server socket
    uploadSocket = socket.socket()
    host = '0.0.0.0'
    uploadSocket.bind((host, c_port))
    uploadSocket.listen(5)
    while 1:
        # Accept an incoming request for upload
        downloadSocket, downloadAddress = uploadSocket.accept()
        message = downloadSocket.recv(1024)
        split_data = message.split('\r\n')

        # Check for BAD REQUEST case
        if len(split_data) == 4 and "GET RFC " in split_data[0] and "Host: " in split_data[1] and "OS: " in split_data[
            2]:
            # Check for VERSION NOT SUPPORTED case
            if 'P2P-CI/1.0' in split_data[0]:
                # Else reply to the request with the requested file data
                request = split_data[0].split(" ")
                if request[0] == 'GET':
                    # Get the request RFC number
                    rfc_number = request[2]

                    # Locate the file and get its data
                    rfc_file_path = os.getcwd() + "/rfc/rfc" + str(rfc_number) + ".txt"
                    opened_file = open(rfc_file_path, 'r')
                    data = opened_file.read()

                    # Formulate the reply to be sent to the requesting peer
                    reply_message = "P2P-CI/1.0 200 OK\r\n" \
                                    "Date: " + str(email.utils.formatdate(usegmt=True)) + "\r\n" \
                                                                                          "OS: " + str(
                        platform.platform()) + "\r\n" \
                                               "Last-Modified: " + str(
                        time.ctime(os.path.getmtime(rfc_file_path))) + "\r\n" \
                                                                       "Content-Length: " + str(len(data)) + "\r\n" \
                                                                                                             "Content-Type: text/plain\r\n"
                    reply_message = reply_message + data

                    # Send the reply
                    downloadSocket.sendall(reply_message)
            else:
                reply_message = "505 P2P-CI Version Not Supported\r\n"
                downloadSocket.send(reply_message)
        else:
            reply_message = "400 Bad Request\r\n"
            downloadSocket.send(reply_message)


def download_thread(req_message, peer_host_name, peer_port_number, rfc_number):
    # Connect to the upload server socket of the peer holding the required file
    requestPeerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    requestPeerSocket.connect((peer_host_name, int(peer_port_number)))

    print("Connection with peer established")

    # Send the GET request to the peer
    requestPeerSocket.sendall(req_message)

    # Receive the reply from the peer with the data in it.
    get_reply = ""
    get_reply = requestPeerSocket.recv(1024)
    if "P2P-CI/1.0 200 OK" in get_reply.split("\r\n")[0]:
        print("P2P-CI/1.0 200 OK")
        content_line = (get_reply.split("\r\n"))[4]
        content_length = int(content_line[content_line.find('Content-Length: ') + 16:])
        get_reply = get_reply + requestPeerSocket.recv(content_length)
        rfc_file_path = os.getcwd() + "/RFC/RFC" + rfc_number + ".txt"
        data = get_reply[get_reply.find('text/plain\r\n') + 12:]

        # Writing the file data to a file
        with open(rfc_file_path, 'w') as file:
            file.write(data)
        print("File Received from peer and stored locally now")
    elif "Version Not Supported" in get_reply.split("\r\n")[0]:
        print(get_reply)
    elif "Bad Request" in get_reply.split("\r\n")[0]:
        print(get_reply)

    # Closing the socket connection
    requestPeerSocket.close()

c_Socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
c_Socket.connect((HOST, PORT))
print('connected to server')
c_hostname = c_Socket.getsockname()
c_port = 60000 + random.randint(1, 1001)
data = pickle.dumps([c_port])
c_Socket.send(data)



#send the initial peer information to the server
rfc_numbers=[]
rfc_titles=[]
rfc_list_dict={}
rfc_storage_path = os.getcwd()+"/rfc"
for file_name in os.listdir(rfc_storage_path):
    if 'rfc' in file_name:
        key=file_name[file_name.find("c")+1:file_name.find(".")]
        rfc_list_dict[key]=file_name
        #for each file, create and send an ADD request
        req_message = add_request(key,rfc_list_dict[key])
        print ("ADD Request to be sent to the server")
        print (req_message)
        information_list = [req_message]
        info_add = pickle.dumps(information_list, -1)
        print (info_add)

while 1:
    user_input = input("Select one of the following : 1 ADD\n 2 GET\n 3 LIST\n 4 LOOKUP\n 5 EXIT\n")

    #ADD
    if user_input == "1":
        # form a request to be sent to the server
        rfc_num=input("Enter RFC number")
        rfc_title=input("Enter RFC title")
        rfc_file_path = os.getcwd() + "/rfc/rfc" + rfc_num + ".txt"
        if os.path.isfile(rfc_file_path):
            # Create the ADD Request message and send it to server using the socket
            client_message_1 = add_request(rfc_num, rfc_title)
            print("ADD Request to be sent to the server")
            print(client_message_1)
            info_add = pickle.dumps([client_message_1], -1)
            c_Socket.send(info_add)

            print("Waiting for a response")
            # Receive the response from server and print the same
            response_received = c_Socket.recv(1024)
            print("ADD Response sent from the server")
            print(response_received)
        else:
            print("File Not Present in the directory")

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
