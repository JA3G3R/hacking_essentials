import paramiko
import os
import sys
from auth_funcs import key_trust,manual_auth,auto_auth
from hexdump import *
import socket
import getopt
import threading
import select
# remote host is the one which is unaccessible to our SSH server sitting outside the firewall
# so we connect to it from our client sitting inside the firewall and that has access to the remote host
# we connect to the "remote host" on "remote port" and tunnel all the data we receive through the secure ssh session over to our
# ssh server outside the firewall

def handler(remote_host,remote_port,chan):
    chan.settimeout(2.0)
    sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    sock.connect((remote_host,remote_port))
    sock.settimeout(2.00)
    print(f"[+] Connected to remote host {remote_host}:{remote_port}")
    
#    r , w , e = select.select([sock,chan],[sock,chan],[])
    while True:
        print(f"[+] Waiting for data from {chan.getpeername()[0]}:{chan.getpeername()[1]}")
        try:
            data = chan.recv(4096)
        except Exception as e:
            print(f"[-] Didn't receive any data : {str(e)}") 
        if not len(data):
            print(f"[-] No data received from {chan.getpeername()[0]}:{chan.getpeername()[1]}\nEXITING!!!")
            break
        print(f" [+] RECVD {len(data)} bytes of data from {chan.getpeername()[0]}:{chan.getpeername()[1]}.")
        sent = sock.send(data)
        print(f'[+] SENT {sent} bytes of data to {remote_host}:{remote_port}')
        
        print(f"[+] Waiting for data from {remote_host}:{remote_port}")
        try:
            data = sock.recv(4096)
        except socket.timeout:
            print("[-] Timeout ... ")
            continue
        if not len(data):
            print(f"[-] No data received from {remote_host}:{remote_port}\nEXITING!!!")
            break
        print(f" [+] RECVD {len(data)} bytes of data from {remote_host}:{remote_port}")
        sent = chan.send(data)
        print(f'[+] SENT {sent} bytes of data to {chan.getpeername()[0]}:{chan.getpeername()[1]}')
    sock.close()
    chan.close()

# This requests a secure tunnel to the ssh-server outside the firewall to send data from the 
# unaccessible remote host inside the firewall through the client

def reverse_forward_tunnel(remote_host,remote_port,transport,forward_port):
    try:
        transport.request_port_forward('',forward_port)
    except paramiko.SSHException:
        print(f"[-] Sorry, but the server does not allow the port {forward_port} to be forwarded\nExiting")
        sys.exit(1)
    try:
        print("[+] Waiting for port forward from ssh server...")
        chan = transport.accept(100)
        print("[+] Got the port!!!")
    except Exception as e:
        print(f"[-] Failed to listen for forwarded channels {str(e)}")
        sys.exit(1)
    if chan is None:
        print("[-] No channel")
        sys.exit(1)
    handler_thread = threading.Thread(target=handler,args=(remote_host,remote_port,chan,))
    handler_thread.start()

def main():
    forward_port = ''
    remote = ''
    server = ''
    username = ''
    try:
        opts,args = getopt.getopt(sys.argv[1:],"R:u:r:s:",["forward-port","remote","server","username"])
    except getopt.GetoptError as e:
        print(f"Cannot parse options {str(e)}")
        sys.exit(1)
    
    for o,a in opts:
        if o in ("--remote","-r"):
            remote = a
        elif o in ("--server","-s"):
            server = a
        elif o in ("--username","-u"):
            username = a
        elif o in ("-R","--forward-port"):
            forward_port = a
        else:
            assert False,"Invalid argument"

    if not len(forward_port) or not len(remote) or not len(server) or not len(username):
        print(f"USAGE : {sys.argv[0]} -R <remote port to forward> -u <username> -s <server_host:server_port> -r <remote_host:remote_port>")
        sys.exit(1)

    forward_port = int(forward_port)

    if remote.find(":") == -1:
        print("Remote host string is in invalid format")
        sys.exit(1)

    remote = remote.split(":")
    remote_host = remote[0]
    if not len(remote_host):
        print("Invalid host")
        sys.exit(1)
    remote_port = int(remote[1])
    if not remote_port:
        print("Invalid port")
        sys.exit(1)

    if server.find(":") == -1:
        print("Server string is in invalid format")
        sys.exit(1)
    server = server.split(":")
    server_host = server[0]
    if not len(remote_host):
        print("Invalid host")
        sys.exit(1)
    server_port = int(server[1])
    if not remote_port:
        print("Invalid port")
        sys.exit(1)

    try:
        sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        sock.connect((server_host,server_port))
    except Exception as e:
        print(f"[-] Failed to connect to SSH server : {str(e)}")
        sys.exit(1)

    try:
        client_t = paramiko.Transport(sock)
        client_t.start_client()
    except paramiko.SSHException as e:
        print(f"[-] Negotiation failed : {str(e)}")

    key_trust(client_t,server_host)
    if not auto_auth(client_t,username):
        manual_auth(client_t,username)
    print("[+] Authenticated...") 
    reverse_forward_tunnel(remote_host,remote_port,client_t,forward_port)
main()
