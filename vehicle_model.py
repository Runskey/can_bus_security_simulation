
from random import random, sample, expovariate
from glob_def import CarEvent, CAN_DATA_RATE, CAN_FRAME_LEN, BUS_LOAD
from dbc_msg_conversion import DbcMsgConvertor
from math import exp

class Vehicle:
    speed = .0
    enginespeed = 1.0
    torque = .0

    max_engine_speed = 5000.0
    min_engine_speed = 0.1

    gas_pedal_to_power_ratio = 1.0
    torque_to_acce_power_ratio = 1.0
    speed_to_enginespeed_ratio = 1.0
    speed_scale = 0.06
    brake_scale = 0.3
    speedometer = []
    tachometer = []
    braking_record = []
    torque_record = []
    dbc_data = None
    def __init__(self, model="unknown", speed=0.0, tacho=0.0):
        self.speed = speed
        self.tacho = tacho
        self.dbc_data = DbcMsgConvertor(model)
        return

    def __get_gear_ratio(self):
        if self.speed <= 0:
            gear_ratio = 1.0
        elif self.speed >= 120:
            gear_ratio = 0.2
        else:
            gear_ratio = (580-4*self.speed)/500.0
        return gear_ratio

    def __record_car_status(self, timestamp):
        self.speedometer.append([timestamp, self.speed])
        self.tachometer.append([timestamp, self.enginespeed])
        return

    def __get_brake_ratio(self, value):
        return exp(value)

    def __audit_engine_speed(self):
        if self.enginespeed > self.max_engine_speed:
            self.enginespeed = self.max_engine_speed
        if self.enginespeed < self.min_engine_speed:
            self.enginespeed = self.min_engine_speed
        return

    def __no_driving_action(self):
        if self.speed == 0:
            return
        speed_change =  self.speed * ((random()-0.7)*0.1)
        self.speed = self.speed + speed_change
        if self.speed <= 0:
            self.speed = 0
        self.enginespeed = self.speed * self.__get_gear_ratio() * self.speed_to_enginespeed_ratio
        self.__audit_engine_speed()
        return

    def record_gas_pedal_action(self, timestamp, value):
        # with engine speed exceeds upper bound, no fuel provided to engine
        if self.enginespeed >= self.max_engine_speed:
            self.__no_driving_action()
        else:
            # 1. Calcuate torque by power and engine speed
            # 2. Calculate accelerating rate by torque and gear ratio
            # 3. Update speed by accelerating rate
            # 4. Update engine speed by speed
            torque = value / self.enginespeed * self.gas_pedal_to_power_ratio
            acce_power = torque * self.__get_gear_ratio() * self.torque_to_acce_power_ratio
            self.speed = self.speed + acce_power
            self.enginespeed = self.speed * self.__get_gear_ratio() * self.speed_to_enginespeed_ratio
            self.__audit_engine_speed()

        self.__record_car_status(timestamp)
        return
    
    def record_brake_pedal_action(self, timestamp, value):
        speed_loss = self.__get_brake_ratio(value)
        self.speed = (self.speed-speed_loss) if (self.speed > speed_loss) else 0.0
        self.enginespeed = self.speed * self.__get_gear_ratio() * self.speed_to_enginespeed_ratio
        self.__audit_engine_speed()

        self.__record_car_status(timestamp)
        self.braking_record.append([timestamp, value])

    def get_speedometer_record(self):
        return self.speedometer
    def get_tachometer_record(self):
        return self.tachometer 
    def get_braking_record(self):
        return self.braking_record


def get_event_timing_from_interval(start_second, stop_second, load_ratio):
    # generate event on random timing point between start_time and stop_time, in unit of ms

    event_number = int(CAN_DATA_RATE/CAN_FRAME_LEN * (stop_second-start_second) * BUS_LOAD * load_ratio)
    timing_interval = range(int(start_second*1e3), int(stop_second*1e3))
    timing_seq = [i*1e-3 for i in sample(timing_interval, event_number)]
    return sorted(timing_seq)

def generate_constant_event(start_time = .0, stop_time = 10.0, acceleration=0):
    event_list = []

    # -----------------------------------------------------
    # create accelaration event
    acce_ratio = 0.2
    time_seq = get_event_timing_from_interval(start_time, stop_time, acce_ratio)

    for i in time_seq:
        event = CarEvent(desc="Accelerating", timestamp=i, ID=CarEvent.CAR_EVENT_GAS_PEDAL, value=random() if acceleration>0 else 0)
        event_list.append(event)

    # -----------------------------------------------------
    # create diagnostic event
    diag_ratio = 0.1
    time_seq = get_event_timing_from_interval(start_time, stop_time, diag_ratio)

    for i in time_seq:
        event = CarEvent(desc="Diagnostic", timestamp=i, ID=CarEvent.CAR_EVENT_BUS_DIAG, value = random())
        event_list.append(event)
    
    return event_list

def generate_sporadic_event(start_time = .0, stop_time = 10.0):
    event_list = []

    # -----------------------------------------------------
    # create braking event
    brak_ratio = 0.03
    braking_interval = 5.0 # braking event average interval

    while True:
        braking_start = expovariate(1.0/braking_interval)

        # Suppose a braking event lasts for 1 second
        if (braking_start + start_time + 1 >= stop_time):
            break
        
        time_seq = get_event_timing_from_interval(start_time+braking_start, start_time+braking_start+1.0, brak_ratio)

        for i in time_seq:
            event = CarEvent(desc="breaking", timestamp=i, ID=CarEvent.CAR_EVENT_BRAKE_PEDAL, value=random())
            event_list.append(event)

    return event_list

def calculate_vehicle_speed(start_time, stop_time, event_list, initial_speed=.0):
    speed_scale = 0.1
    current_speed = initial_speed
    current_time = start_time
    speed_list = [current_speed]
    for i in event_list:
        if i.ID == CarEvent.CAR_EVENT_GAS_PEDAL:
            current_speed = current_speed + speed_scale * i.value

        # one second elapsed
        if i.timestamp > (current_time+1):
            current_time = current_time + 1
            speed_list.append(current_speed)

    return speed_list

def calculate_vehicle_odometer(start_time, stop_time, event_list, initial_speed=.0):
    odometer_list = []
    return odometer_list