import socket
import os
#not complete, use ARP discoverer
#(included in this repository with name 
#"host_discovery_with_scapy_and_arp.py") instead
#however this method is preferred for quick scan of the
#network as UDP packets are lighter than ARP requests
HOST = '192.168.1.45'

if os.name == 'nt':
    socket_protocol = socket.IPPROTO_IP;
else:
    socket_protocol = socket.IPPROTO_ICMP;  

sniffer = socket.socket(socket.AF_INET,socket.SOCK_RAW,socket_protocol)

sniffer.bind((HOST,0))
sniffer.setsockopt(socket.IPPROTO_IP,socket.IP_HDRINCL,1)
if os.name == 'nt':
    sniffer.ioctl(socket.SIO_RCVALL,socket.RCVALL_ON)

data = sniffer.recvfrom(65535)

print(data)

if os.name == 'nt':
    sniffer.ioctl(socket.SIO_RCVALL,socket.RCVALL_OFF)



