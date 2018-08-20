from glob_def import CarEvent
from scapy.layers.can import CAN
from scapy.layers.inet import IP, UDP
from scapy.utils import wrpcap, rdpcap
from vehicle_model import Vehicle
from dbc_msg_conversion import DbcMsgConvertor

import struct


def write_car_event_to_can_packet(car: Vehicle, event_list: CarEvent):
    pkt_list = []
    for event in event_list:
        if event.ID == CarEvent.CAR_EVENT_FREE:
            continue
        data = car.dbc_data.simple_msg_encode(event.ID, event.value)

        # extend to 8 bytes by padding zero
        data = data+'00'*(8-car.dbc_data.get_msg_length_in_byte(event.ID))

        byte0, byte1, byte2, byte3, byte4, byte5, byte6, byte7 = \
            int(data[0:2], 16), \
            int(data[2:4], 16), \
            int(data[4:6], 16), \
            int(data[6:8], 16), \
            int(data[8:10], 16), \
            int(data[10:12], 16), \
            int(data[12:14], 16), \
            int(data[14:], 16)

        can_payload = \
            struct.pack('<8B', byte0, byte1, byte2, byte3,
                        byte4, byte5, byte6, byte7)
        pkt = CAN(identifier=event.ID, length=len(data), data=can_payload)
        pkt.time = event.timestamp
        pkt_list.append(pkt)

    wrpcap("can_packet.pcap", pkt_list)
    return


def write_car_event_to_udp_packet(car: Vehicle,
                                  event_list: CarEvent,
                                  src_ip="192.168.3.31",
                                  dst_ip="192.168.3.1",
                                  src_port=1236,
                                  dst_port=0x0cb0):
    # UDP packet format is defined in:
    # National Instrument. Compact RIO Reference and Procedures
    # (FPGA Interface).
    # https://zone.ni.com/reference/en-XX/help/370984T-01/, 2016.
    # [Online; accessed 5-April-2016]

    # | MSB     | ...     | ...     | LSB        |
    # | Timestamp (upper U32)                    |
    # | Timestamp (lower U32)                    |
    # | Identifier                               |
    # | Type    | InfoA   | InfoB   | DataLength |
    # | Data[0] | Data[1] | Data[2] | Data[3]    |
    # | Data[4] | Data[5] | Data[6] | Data[7]    |

    pkt_list = []
    for event in event_list:
        if event.ID == CarEvent.CAR_EVENT_FREE:
            continue
        if event.ID == CarEvent.CAR_EVENT_GAS_ACC_VIA_ICE:
            # pre-process the message value
            event.value = (0x58 << 16) + event.value*0xFFFF

        data = car.dbc_data.simple_msg_encode(event.ID, event.value)
        # convert data into 8 bytes
        data = data+'00'*(8-car.dbc_data.get_msg_length_in_byte(event.ID))
        byte0, byte1, byte2, byte3, byte4, byte5, byte6, byte7 = \
            int(data[0:2], 16), \
            int(data[2:4], 16), \
            int(data[4:6], 16), \
            int(data[6:8], 16), \
            int(data[8:10], 16), \
            int(data[10:12], 16), \
            int(data[12:14], 16), \
            int(data[14:], 16)

        udp_time_upper32 = int(event.timestamp*1e3) >> 32
        udp_time_lower32 = int(event.timestamp*1e3) & 0xffffffff
        udp_identifier = car.dbc_data.get_msg_can_id(event.ID)
        udp_type = 0x0
        udp_infoA = 0x05
        udp_infoB = 0x05
        udp_datalen = car.dbc_data.get_msg_length_in_byte(event.ID)

        udp_payload = struct.pack('<3I4B8B',
                                  udp_time_upper32,
                                  udp_time_lower32,
                                  udp_identifier,
                                  udp_type,
                                  udp_infoA, udp_infoB, udp_datalen,
                                  byte0, byte1, byte2, byte3,
                                  byte4, byte5, byte6, byte7)
        pkt = IP(src=src_ip, dst=dst_ip) \
            / UDP(sport=src_port, dport=dst_port) \
            / udp_payload
        pkt.time = event.timestamp
        pkt_list.append(pkt)

    wrpcap("udp_packet.pcap", pkt_list)
    # send(pkt, inter=1, count=5)
    return


def read_car_event_from_udp_packet(car: Vehicle) -> CarEvent:
    # UDP packet format is defined in:
    # National Instrument. Compact RIO Reference and Procedures
    # (FPGA Interface).
    # https://zone.ni.com/reference/en-XX/help/370984T-01/, 2016.
    # [Online; accessed 5-April-2016]

    # | MSB     | ...     | ...     | LSB        |
    # | Timestamp (upper U32)                    |
    # | Timestamp (lower U32)                    |
    # | Identifier                               |
    # | Type    | InfoA   | InfoB   | DataLength |
    # | Data[0] | Data[1] | Data[2] | Data[3]    |
    # | Data[4] | Data[5] | Data[6] | Data[7]    |

    event_out = []
    pkt_list = rdpcap("udp_packet.pcap")

    for pkt in pkt_list:
        udp_pkt = pkt[UDP]

        udp_time_upper32, udp_time_lower32, udp_identifier, \
            udp_type, udp_infoA, udp_infoB, udp_datalen, \
            byte0, byte1, byte2, byte3, byte4, byte5, byte6, byte7 \
            = struct.unpack('<3I4B8B', udp_pkt.payload.original)

        event_id = car.dbc_data.get_event_id_by_can_id(udp_identifier)
        if event_id == CarEvent.CAR_EVENT_UNKNOWN:
            # ignore unknown event
            continue

        event_time = ((udp_time_upper32 << 32) + udp_time_lower32) * 1e-3
        hex_str = '{0:02x}{1:02x}{2:02x}{3:02x}{4:02x}{5:02x}{6:02x}{7:02x}' \
            .format(byte0, byte1, byte2, byte3, byte4, byte5, byte6, byte7)
        event_value = car.dbc_data.simple_msg_decode(event_id, hex_str)

        event_out.append(CarEvent(desc="", timestamp=event_time,
                                  ID=event_id, value=event_value))

    return event_out


if __name__ == '__main__':
    pass
