from ctypes import *
import socket
import struct as st

class IP(Structure):
    _fields_ = [('ver',c_ubyte,4),('hlen',c_ubyte,4),('tos',c_ubyte,8),('tlen',c_ushort,16),('hid',c_ushort,16),('flags',c_ubyte,3),('off',c_ushort,13),('ttl',c_ubyte,8),('prot',c_ubyte,8),('chk',c_ushort,16),('src',c_uint,32),('dst',c_uint,32),('opt',c_uint,32)]
    
    def __new__(cls,buff):
        return cls.from_buffer_copy(buff)
    def __init__(self,buff):
        self.src_address = socket.inet_ntoa(st.pack("<L",self.src))
        self.dst_address = socket.inet_ntoa(st.pack("<L",self.dst))

sniffer = socket.socket(socket.AF_INET,socket.SOCK_RAW,socket.IPPROTO_ICMP)
sniffer.setsockopt(socket.IPPROTO_IP,socket.IP_HDRINCL,1)
sniffer.bind(('192.168.1.45',0))
buff = sniffer.recvfrom(65535)
ip_hdr = IP(buff[0])
print(ip_hdr.src_address)

