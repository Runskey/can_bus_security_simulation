#from scapy.all import IP, UDP, send

from glob_def import CanEvent
from scapy.layers.can import CAN
from scapy.layers.inet import IP, UDP
from scapy.utils import wrpcap
import struct

def write_can_packet(event_list:CanEvent):
    pkt_list = []
    for event in event_list:
       # pkt = Ether()/IP(dst='192.168.31.250')/
       data = struct.pack('=f', event.value)
       pkt = CAN(identifier=event.ID, length=8, data=data)
       pkt.time = event.timestamp
       pkt_list.append(pkt)

    wrpcap("can_packet.pcap", pkt_list)

    return

def write_udp_packet(event_list):
    pass

if __name__ == '__main__':
    data = struct.pack('=BHI', 0x12, 20, 1000)
    pkt = IP(src='192.168.1.81', dst='192.168.1.10')/UDP(sport=12345, dport=55555)/data
    send(pkt, inter=1, count=5)