import threading
import socket
import sys
def modify_response(response):
    #use this function to modify all the responses sent back to the client
    return response

def modify_request(request):
    #use this function to modify all the requests sent to the server
    return request

def recieve_from(sock):
    recv_len=1
    to_send = b''
    while recv_len:
        data = sock.recv(4096)
        recv_len = len(to_send)
        to_send += data
    return to_send


def proxy_handler(client_sock,remote_host,remote_port,receive_first):
    remote_sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    try:
        remote_sock.connect((remote_host,remote_port))
    except Exception as err:
        print(str(err))
        print("[*] Sorry can't connect to the remote host. Try again later")

    if receive_first:
        got_this = recieve_from(remote_sock)
        if len(got_this):
            print("Orginal Response --->")
            print("Got This --> ",got_this)
            print("---------------------")
            got_this = modify_response(got_this)
            print("Modified Response --->:")
            print("Got This --> ",got_this)
            print("---------------------")
            client_sock.send(got_this)
            print("<=== SENT TO CLIENT")
 
    while True:

        to_send=recieve_from(client_sock)
        if len(to_send):
            print("Orginal Request --->")
            print("To send --->",to_send)
            print("---------------------")
            to_send = modify_request(to_send)
            print("Modified Request --->:")
            print("To send --->",to_send)
            print("---------------------")
            remote_sock.sendall(to_send)
            print("===> SENT TO REMOTE")
        else:
            client_sock.close()
            remote_sock.close()


        got_this = recieve_from(remote_sock)
        if len(got_this):
            print("Orginal Response --->")
            print("Got This --> ",got_this)
            print("---------------------")
            got_this = modify_response(got_this)
            print("Modified Response --->:")
            print("Got This --> ",got_this)
            print("---------------------")
            client_sock.send(got_this)
            print("<=== SENT TO CLIENT")
        else:
            client_sock.close()
            remote_sock.close()

def server_loop(local_host,local_port,remote_host,remote_port,receive_first):

    local = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    try:
        local.bind((local_host,local_port))
    except Exception as err:
        print("[*] Can't setup server at {}:{}".format(local_host,local_port))
        print(str(err))
    print("[*] Listening on {}:{}".format(local_host,local_port))
    while True:
        local.listen(5)
        client,client_port = local.accept()
        print("[*] Got connection from {}:{}".format(client.getpeername()[0],client.getpeername()[1]))
        
        client_thread = threading.Thread(target=proxy_handler,args=(client,remote_host,remote_port,receive_first,))
        client_thread.start()

def main():
    
    if not len(sys.argv[1:]) == 5:
        print("<USAGE> {} local_host local_port remote_host remote_port receive_first".format(sys.argv[0]))
        print("Eg. {} 127.0.0.1 12345 10.0.1.18 9000 True".format(sys.argv[0]))
        sys.exit(1)

    local_host = sys.argv[1]
    local_port = int(sys.argv[2])

    remote_host = sys.argv[3]
    remote_port = int(sys.argv[4])

    receive_first = sys.argv[5]

    server_loop(local_host,local_port,remote_host,remote_port,receive_first)
main()

