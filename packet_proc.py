#from scapy.all import IP, UDP, send

from glob_def import CanEvent
from scapy.layers.can import CAN
from scapy.layers.inet import IP, UDP
from scapy.utils import wrpcap
from vehicle_model import Vehicle
from dbc_msg_conversion import DbcMsgConvertor

import struct

def write_can_packet(car:Vehicle, event_list:CanEvent):
    pkt_list = []
    for event in event_list:
        data = car.dbc_data.simple_msg_encode(event.ID, event.value)
        pkt = CAN(identifier=event.ID, length=len(data), data=data)
        pkt.time = event.timestamp
        pkt_list.append(pkt)
    
    wrpcap("can_packet.pcap", pkt_list)
    return

def write_udp_packet(car:Vehicle, event_list:CanEvent, src_ip, dst_ip, src_port=1236, dst_port=0x0cb0):
    pkt_list = []
    for event in event_list:
        data = car.dbc_data.simple_msg_encode(event.ID, event.value)
        pkt = IP(src=src_ip, dst=dst_ip)/UDP(sport=src_port, dport=dst_port)/data
        pkt_list.append(pkt)

    wrpcap("udp_packet.pcap", pkt_list)
    # send(pkt, inter=1, count=5)
    return

if __name__ == '__main__':
    data = struct.pack('=BHI', 0x12, 20, 1000)
    pkt = IP(src='192.168.1.81', dst='192.168.1.10')/UDP(sport=12345, dport=55555)/data
    send(pkt, inter=1, count=5)