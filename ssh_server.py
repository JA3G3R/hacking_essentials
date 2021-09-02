import paramiko
from getpass import getpass
import sys
import os
import socket


class Server(paramiko.ServerInterface):
    def check_auth_publickey(self,username,key):
        if key.get_name == 'ssh-rsa':
            auth_keys = paramiko.RSAKey.from_private_key_file(os.path.expanduser("~/.ssh/authorized_keys"))
            for key in auth_keys:
                if key.__cmp__(key) == 0:
                    return paramiko.AUTH_SUCCESSFUL
            return paramiko.AUTH_FAILED

        elif key.get_name == 'ssh-dsa':
            auth_keys = paramiko.DSSKey.from_private_key_file(os.path.expanduser("~/.ssh/authorized_keys"))
            for key in auth_keys:
                if key.__cmp__(key) == 0:
                    return paramiko.AUTH_SUCCESSFUL
            return paramiko.AUTH_FAILED
        elif key.get_name == 'ssh-ecdsa':
            auth_keys = paramiko.ECDSAKey.from_private_key_file(os.path.expanduser("~/.ssh/authorized_keys"))
            for key in auth_keys:
                if key.__cmp__(key) == 0:
                    return paramiko.AUTH_SUCCESSFUL
            return paramiko.AUTH_FAILED
        elif key.get_name == 'ssh-ed25519':
            auth_keys = paramiko.Ed25519Key.from_private_key_file(os.path.expanduser("~/.ssh/authorized_keys"))
            for key in auth_keys:
                if key.__cmp__(key) == 0:
                    return paramiko.AUTH_SUCCESSFUL
            return paramiko.AUTH_FAILED

    def check_auth_password(self,username,passwd):
        if username == 'kali' and passwd == '1234':
            return paramiko.AUTH_SUCCESSFUL
        elif username == 'bhavarth' and passwd == 'password':
            return paramiko.AUTH_SUCCESSFUL
        else:
            return paramiko.AUTH_FAILED

    def check_channel_request(self,kind,chanid):
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
        else:
            return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED
try:
    host_key = paramiko.RSAKey(filename = os.path.expanduser("~/.ssh/id_rsa"))
except paramiko.PasswordRequiredException:
    try:
        pwd = getpass("Enter passphrase to the encrypted private key [~/.ssh/id_rsa]: ")
        host_key = paramiko.RSAKey(filename = os.path.expanduser("~/.ssh/id_rsa"),password = pwd)
    except paramiko.SSHException:
        print("Incorrect Passphrase!\nExiting")
        sys.exit(1)

if len(sys.argv) < 2:
    print(f"USAGE: {sys.argv[0]} <port>")
    sys.exit(1)
port = int(sys.argv[1])
server_sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
try:
    server_sock.bind(("",port))
    server_sock.listen(10)
    print(f"[+] Listening on port : {port}")
    client_sock,addr = server_sock.accept()	    
    print(f"[+] Got connection from {addr[0]}:{addr[1]}")
except Exception as e:
    print(f"Failed to listen on port: {port} : {str(e)}")
    sys.exit(1)

client_t = paramiko.Transport(client_sock)
client_t.add_server_key(host_key)
server = Server()
try:
    client_t.start_server(server = server)
except SSHException:
    print('SSH negotiation failed')
    sys.exit(1)
client_channel = client_t.accept(120)
client_channel.settimeout(15)
if client_channel is None:
    print("*** No Channel")
    sys.exit(1)
print("[+] Authenticated")
recvd = client_channel.recv(4096)
print(recvd.decode())
client_channel.send("Welcome to Bhavarth's SSH server!!!")
try:
    while True:
        cmd = input("Enter the command: ")
        cmd = bytes(cmd,'utf-8')
        print(f"<== Sent : {cmd}") 
        client_channel.send(cmd)
        recvd = client_channel.recv(4096)
        print(recvd.decode())
except KeyboardInterrupt:
    print("Shutting Down...")
    client_channel.close()
    client_t.close()
    client_sock.close()
    print("Bye!")
    sys.exit(1)
