from scapy.all import Ether,ARP,srp
import datetime
import ipaddress
import sys

hosts_up = list()
HOST = '192.168.1.49'
def get_mac(ip):
    try:
        packet = Ether(dst='ff:ff:ff:ff:ff:ff')/ARP(op='who-has',pdst=ip)
        resp,_ = srp(packet,timeout=0.5,retry=0,verbose=False)
        print(f"Sent ARP request to {ip}")
        for _,r in resp:
            return r[Ether].src
        return None
    except KeyboardInterrupt:
        sys.exit(1)

def discover(subnet):
    try:
        for host in ipaddress.ip_network(subnet).hosts():
            if not str(host) == HOST:
                hwaddr = get_mac(str(host))
                if not hwaddr is None:
                    with open('hosts_up','a') as h:
                        h.write(f"\nHost up : {host}")
                    hosts_up.append(str(host))
                    print(f"Host Up: {host}")

    except KeyboardInterrupt:
        sys.exit(1) 
    finally:
        print('\n'+'-'*15+'SUMMARY'+'-'*15+'\n')
        print(f"Hosts up : {len(hosts_up)}")
        for host in hosts_up:
            print(f"Host up : {host}")
        with open('hosts_up','a') as h:
            h.write('\n')

if __name__ == "__main__":
    with open('hosts_up','w') as h: 
        h.write('-'*15+'SUMMARY'+'-'*15+'\n')
        h.write(str(datetime.datetime.now()))
    discover('192.168.1.0/24')
    
