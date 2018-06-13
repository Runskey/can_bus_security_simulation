
# Global variables

CAN_VERSION = '2.0B'
CAN_DATA_RATE = 1e6 # CAN bus 2.0B data rate = 1Mbps
CAN_FRAME_LEN = 128 # Exten
BUS_LOAD = 0.3

# CAN ID Definition
CAN_ID_ACCE = 0x1ab
CAN_ID_BRAK = 0x55
CAN_ID_DIAG = 0x7d3

# class definition
class CanEvent:
    timestamp = .0
    desc = ""
    ID = 0
    value = 0

    def __init__(self, desc="Invalid", timestamp=0, ID=-1, value = -1):
        self.timestamp = timestamp
        self.desc = desc
        self.ID = ID
        self.value = value