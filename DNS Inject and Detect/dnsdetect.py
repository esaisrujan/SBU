from scapy.all import *
import argparse
import datetime
from scapy.layers.dns import *
from scapy.layers import *
import netifaces as ni
d=dict()
def dnsSpoof(pkt):

        if  pkt.haslayer(DNSRR):
                if pkt[DNS].qd.qtype == 1:
                        iplist = []
                        for x in range(pkt[DNS].ancount):
                            if pkt[DNS].an[x].type == 1 and pkt[DNS].an[x].rdata not in iplist:
                                iplist.append(pkt[DNS].an[x].rdata)
                        
                        try:
                            if  len(iplist)>0 :#and len(d[pkt[DNS].id])<2:
                                
                                d[pkt[DNS].id].append([pkt[Ether].src,iplist])
                                temp = []
                                for x in d[pkt[DNS].id]:
                                      if x not in temp:
                                            temp.append(x)
                                             
                                d[pkt[DNS].id] = temp
                                if len(d[pkt[DNS].id])>1 and d[pkt[DNS].id][-1][0]!=d[pkt[DNS].id][-2][0]:
                                    print(datetime.datetime.fromtimestamp(pkt.time).strftime('%Y-%m-%d %H:%M:%S:%f')," DNS Poisining Attempt") 
                                    print("TXID "+str(pkt[DNS].id)+" Request "+str(pkt[DNSQR].qname)[2:-2])
                                    for i,x in  enumerate(d[pkt[DNS].id]):
                                         print("Answer  "+str(i+1)+" ", x[1])
                                    del d[pkt[DNS].id]
                        except KeyError:
                            if len(iplist)>0:
                                d[pkt[DNS].id]= [[pkt[Ether].src,iplist]]
                        
			
if __name__ == '__main__':
        parser = argparse.ArgumentParser(description='arg parser')
        parser.add_argument('-i', metavar=None,
                        help = 'Listen on network device <interface> (e.g., eth0). ')
        parser.add_argument('-r', metavar=None)
        parser.add_argument('expression', nargs='*', action="store")
        args = parser.parse_args()
        rfile=""
        if args.r!= None:
                 rfile = args.r
        if len(args.expression)>0:
                expression = " ".join(args.expression)
        else:
                expression = ""
        if args.i == None:
                dev = ni.gateways()['default'][ni.AF_INET][1]
        else:
                dev = args.i
        print(dev)
        print(expression)
        print(rfile)
        if rfile == "":
        	sniff(iface = dev,filter=expression, prn=dnsSpoof, store =0)
        else:
                sniff(offline = rfile , iface = dev, filter = expression, prn = dnsSpoof)
