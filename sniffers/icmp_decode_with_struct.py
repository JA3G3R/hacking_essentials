import struct as st
import socket
import os

if os.name == 'nt':
    socket_proto = socket.IPPROTO_IP
else:
    socket_proto = socket.IPPROTO_ICMP
sniff = socket.socket(socket.AF_INET,socket.SOCK_RAW,socket.IPPROTO_ICMP)
sniff.setsockopt(socket.IPPROTO_IP,socket.IP_HDRINCL,1)
if os.name == 'nt':
    sniff.ioctl(socket.SIO_RCVALL,socket.RCVALL_ON)
sniff.bind(("",0))
buff = sniff.recvfrom(65535)
prot_map = {1 : 'ICMP',6 : 'TCP', 17 : 'UDP'}
class ip:
    def __init__(self,buff):
        header = st.unpack("<BBHHHBBHII",buff[0][0:20])
        self.version = header[0] >> 4
        self.hlen = header[0] & 0xf0
        self.tos = header[1]
        self.total = header[2]
        self.id = header[3]
        self.flags = header[4] & 0x07
        self.offset = header[4] & ~0xfff8
        self.ttl = header[5]
        self.proto  = prot_map[header[6]]
        self.chksum = header[7]
        self.src = socket.inet_ntoa(st.pack("<L",header[8]))
        self.dst = socket.inet_ntoa(st.pack("<L",header[9]))
while True:
    try:
        packet_header = ip(buff)
        print("%s %s -> %s , packet len : %d"%(packet_header.proto,packet_header.src,packet_header.dst,packet_header.total))
        buff = sniff.recvfrom(65535)
    except KeyboardInterrupt:
        
        sniff.ioctl(socket.SIO_RCVALL,socket.RCVALL_OFF)
    except Exception as e:
        print(f"[-] Got error {str(r)}")
        sniff.ioctl(socket.SIO_RCVALL,socket.RCVALL_OFF)
        

if os.name == 'nt':
    sniff.ioctl(socket.SIO_RCVALL,socket.RCVALL_OFF)
    
