import socket
import os
import sys

if len(sys.argv) < 3:
        print(f"Usage {sys.argv[0]} <host> <port>")
        sys.exit(1)

with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as client:
    client.connect((sys.argv[1],int(sys.argv[2])))
    client.send(b'Hey Server,Let\'s talk!')
    recvd = 1
    data = b''
    while recvd:
        recv =  client.recv(4096)
        data+= recv
        print(data.decode())
        to_send = input("Send something: ")
        client.send(bytes(to_send,'utf-8'))
        recvd = len(data)
        data = b''
    print("No data received from the server\nExiting!!!")
