
# Global variables

CAN_VERSION = '2.0B'
CAN_DATA_RATE = 1e6 # CAN bus 2.0B data rate = 1Mbps
CAN_FRAME_LEN = 128 # Exten
BUS_LOAD = 0.3

ACCE_RATIO = 0.2

# class definition
class CarEvent:
    # car event definition
    CAR_EVENT_GAS_PEDAL = 0x101
    CAR_EVENT_BRAKE_PEDAL = 0x102
    CAR_EVENT_BRAKE_SENSOR = 0x103

    CAR_EVENT_BUS_DIAG = 0x203

    CAR_EVENT_RPM = 0x301
    CAR_EVENT_SPEED = 0x302

    timestamp = .0
    desc = ""
    ID = 0
    value = 0

    def __init__(self, desc="Invalid", timestamp=0, ID=-1, value = -1):
        self.timestamp = timestamp
        self.desc = desc
        self.ID = ID
        self.value = value