import socket
import threading
import sys

def client_handler(client_sock):
    data = client_sock.recv(4096)
    print(data.decode())
    while len(data):
        client_sock.send(bytes(f"why did you send me {data.decode()}",'utf-8'))
        data = client_sock.recv(4096)
        print(f"Client sent: {data.decode()}")

    client_sock.send(b"No data sent\nExiting...")
    print(f"Disconnecting from {client_sock.getpeername()[0]}:{client_sock.getpeername()[1]}")

    client_sock.close()

def main():
    if len(sys.argv) < 2:
        print(f"Usage : {sys.argv[0]} <port to bind to>")
        sys.exit(1)
    server_sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    try:
        server_sock.bind(('',int(sys.argv[1])))
        server_sock.listen(10)
        print(f"[+] Listening on port {sys.argv[1]}")
    except OSError as e:
        print(f"[-] Failed to listen on socket: {str(e)}")
        sys.exit(1)
    while True:
        client_sock,addr = server_sock.accept()
        print(f"[+] Got connection from {client_sock.getpeername()[0]}:{client_sock.getpeername()[1]}")
        thread = threading.Thread(target = client_handler,args = (client_sock,))
        thread.start()

main()
