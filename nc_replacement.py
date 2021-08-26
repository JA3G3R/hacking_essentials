#! /usr/bin/python3
import socket
import sys
import subprocess
import getopt
import threading

target = ""
port = 0
listen = False
upload = ""
command = False
cmd_to_exe = ""

def client_send(inp):
    client = socket.socket(socket.AF_INET,socket.SOCK_STREAM) 
    try:
         client.connect((target,port))
         while True:        
            recv_len = 1
            data = b""
            while recv_len:
                recv = client.recv(4096)
                data += recv
                recv_len = len(data)
                if recv_len < 4096:
                    break
            print(data.decode(),end='')
         
            inp = input()
            inp += '\n'
            b = b''
            b = bytes(inp,'utf-8')
            client.sendall(b)


    except Exception as err:
        print(str(err))
        print("[*] Err connection was broken")
        client.close()

def run_command(cmd):
    cmd.rstrip()
    try:
        command_out = subprocess.check_output(cmd,stderr=subprocess.STDOUT,shell=True)
        return command_out
    except subprocess.SubprocessError as err:
        print(str(err))


def client_handler(client_socket):
    global upload,cmd_to_exe,command
    client_host = client_socket.getpeername()[0]
    client_port = client_socket.getpeername()[1]
    if len(upload):
        client_socket.sendall(b'Attempting to create file for reading and writing....\r\n')
        up_fd = open(upload,"wb")
        client_socket.send(b'File opened!\nWrite to it-->')
        while True:
            data = client_socket.recv(4096)
            if not data or data[:3] == b'\r\n':
                break
            else:
                up_fd.write(data)
        up_fd.close()
        client_socket.sendall(b'Successfully created and written to file !!!\n\r')

    if len(cmd_to_exe):
        
        cmd_out = run_command(cmd_to_exe)
        client_socket.send(cmd_out)

    if command:

        try:
            while True:
                client_socket.sendall(b"(NCRpv1.0)<NCRp:#>")
                cmd_in = client_socket.recv(1024)

                if b'\n' in cmd_in:
                    if b'\r\n' in cmd_in:
                        cmd_in = cmd_in[:-2]
                    else:
                        cmd_in = cmd_in[:-1]
                    print("[*] {}:{} executed the command {}".format(client_socket.getpeername()[0],client_socket.getpeername()[1],cmd_in))
                
                    shell_out = run_command(cmd_in)
                    client_socket.sendall(shell_out)
        except Exception as err:
            print(str(err))
            print("Connection aborted for {}:{}".format(client_host,client_port))


    client_socket.close() 

def server_loop():
    global target,port
    server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    if not len(target):
        target = "0.0.0.0"
    if not port > 0:
        port = 1984

    server.bind((target,port))
    while True:
        server.listen(5)
        client , client_port = server.accept()
        print("[*] received connection from {}:{}".format(client_port[0],client_port[1]))
        handle_client = threading.Thread(target=client_handler,args=(client,))
        handle_client.start()
 
def main():
    opts=()
    global target,port,listen,upload,command

    try:
        opts,args = getopt.getopt(sys.argv[1:],"clp:u:t:e:",["listen","port","upload","command","target","execute"])
    except getopt.GetoptError as err:
        print(str(err))

    for o,a in opts:
        if o in ("-l","--listen"):
            listen = True
        elif o in ("-p","-port"):
            port = int(a)
        elif o in ("-u","--upload"):
            upload = a
        elif o in ("-c","--command"):
            command = True
        elif o in ("-t","--target"):
            target = a
        elif o in ("-e","--execute"):
            cmd_to_exe = a
        else:
            assert False,"Argument not recognised"

    if not listen and len(target) and port > 0:
        inp = b'' 
        #ksys.stdin.read()
        client_send(inp)

    if listen:
        server_loop()

main()
