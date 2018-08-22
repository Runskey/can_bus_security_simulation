from enum import Enum
from time import time
import logging

# Global variables
CAN_VERSION = '2.0B'
CAN_DATA_RATE = 1e6  # CAN bus 2.0B data rate = 1Mbps
CAN_FRAME_LEN = 128  # Exten
BUS_LOAD = 0.3

ACCE_RATIO = 0.2
BRAK_RATIO = 0.03
DOS_RATIO = 0.9

# Simulation time, in unit of second
SIMULATION_START_TIME = 0.0
SIMULATION_DURATION = 20
# TIME_OFFSET = time()
TIME_OFFSET = 0.0

# Simulation status control
SIMULATION_GENERATE_CAR_DATA = True
SIMULATION_ANALYZE_CAR_DATA = False
SIMULATION_SHOW_ANIMATION = False

ATTACK_TYPE_DDOS = 0
ATTACK_TYPE_REVERSE_GAS = 1
ATTACK_TYPE_KILL_ENGINE = 2


class CarStatus(Enum):
    NORMAL = 0
    DOS_DETECTED = 1
    ENGINE_SHUTDOWN = 2
    REVERSE_HIGH_FUEllING = 3


class GearShiftStatus(Enum):
    PARK = 0
    REVERSE = 1
    NEUTRAL = 2
    DRIVE = 3
    ENGINEER_BRAKE = 4


class AttackModel:
    def __init__(self):
        self.type = 'unknown'
        self.is_gearshift_check = False
        self.is_speed_check = False
        self.speed_low = -1
        self.speed_high = 1e3

    def __str__(self):
        str_info = f"\
Type: {self.type}; \
Speed_set:{self.is_speed_check}; \
Gear_set:{self.is_gearshift_check}; \
Speed_low:{self.speed_low}; \
Speed_hight:{self.speed_high}"
        return str_info


# class definition
class CarEvent:
    # car event definition
    CAR_EVENT_FREE = 0x100
    CAR_EVENT_GAS_PEDAL = 0x101
    CAR_EVENT_BRAKE_PEDAL = 0x102
    CAR_EVENT_BRAKE_SENSOR = 0x103
    CAR_EVENT_GAS_ACC_VIA_ICE = 0x110

    CAR_EVENT_BROADCAST_GEAR_STATUS = 0x202
    CAR_EVENT_BUS_DIAG = 0x203

    CAR_EVENT_QUERY_RPM = 0x301
    CAR_EVENT_QUERY_SPEED = 0x302
    CAR_EVENT_QUERY_TORQUE = 0x303

    CAR_EVENT_STEERING_WHEEL_ANGLE = 0x400
    CAR_EVENT_PCS_PRECOLLISION = 0x500

    CAR_EVENT_UNKNOWN = 0xffff

    timestamp = .0
    desc = ""
    ID = 0
    value = 0

    def __init__(self, desc="Invalid", timestamp=0, ID=-1, value=-1):
        self.timestamp = timestamp
        self.desc = desc
        self.ID = ID
        self.value = value


def console_out(logFilename):
    ''' Output log to file and console '''
    # Define a Handler and set a format which output to file
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s : %(levelname)s  %(message)s',
        datefmt='%Y-%m-%d %A %H:%M:%S',
        filename=logFilename,
        filemode='w')
    # Define a Handler and set a format which output to console
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s  %(filename)s : %(levelname)s  %(message)s')
    console.setFormatter(formatter)
    # Create an instance
    logging.getLogger().addHandler(console)