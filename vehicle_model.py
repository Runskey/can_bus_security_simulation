
from random import seed, random, sample, expovariate, randint
from glob_def import CarEvent, CarStatus, CAN_DATA_RATE, CAN_FRAME_LEN
from glob_def import BUS_LOAD, ACCE_RATIO, BRAK_RATIO, DOS_RATIO
from dbc_msg_conversion import DbcMsgConvertor
from math import exp


class Vehicle:

    max_engine_speed = 5000.0   # unit: RPM
    min_engine_speed = 100.0    # unit: RPM
    max_torque = 250.0          # unit: Nm
    max_delta_speed = 8.0       # max speed increment in 1 second

    # max speed increment to a scaling factor
    max_acce_power = max_delta_speed*1e-3/BUS_LOAD/ACCE_RATIO

    # map pedal position [0,1] to power [0,70]Kw
    gas_pedal_to_power_ratio = 70.0

    # map speed[kmp] to engine speed[rpm]
    speed_to_enginespeed_ratio = 44.20

    # map torque to accelerator factor
    torque_to_acce_power_ratio = max_acce_power/max_torque/3.0

    speed_elapsing_factor = 3.35e-4
    power_elapsing_factor = 5.18e-4

    invalid_msg_threshold = 1e2

    brake_scale = 0.3

    dbc_data = None

    def __init__(self, model="unknown", speed=0.0):
        self.model = model
        self.speed = speed
        self.enginespeed = Vehicle.min_engine_speed
        self.power = .0
        self.torque = 70.0
        self.dbc_data = DbcMsgConvertor(model)
        self.speedometer = []
        self.tachometer = []
        self.braking_record = []
        self.torquemeter = []
        self.accpower_record = []
        self.status_record = []

        self.status = CarStatus.NORMAL
        self.hpmsg = 0
        self.rlengine = 0
        self.driving_int = -1

        # set random seed
        seed(1)
        return

    def __get_gear_ratio(self):

        def linear_interp(x1, x2, y1, y2, x):
            return (y1*(x-x2)-y2*(x-x1))/(x1-x2)
        # 1
        if self.speed <= 15.0:
            gear_ratio = 3.545
        elif 15.0 < self.speed <= 20.0:
            gear_ratio = linear_interp(15.0, 20.0, 3.545, 1.956, self.speed)
        # 2
        elif 20.0 < self.speed <= 30.0:
            gear_ratio = 1.956
        elif 30.0 < self.speed <= 40.0:
            gear_ratio = linear_interp(30.0, 40.0, 1.956, 1.303, self.speed)
        # 3
        elif 40.0 < self.speed <= 55.0:
            gear_ratio = 1.303
        elif 55.0 < self.speed <= 60.0:
            gear_ratio = linear_interp(55.0, 60.0, 1.303, 0.892, self.speed)
        # 4
        elif 60.0 < self.speed <= 70.0:
            gear_ratio = 0.892
        elif 70.0 < self.speed <= 80.0:
            gear_ratio = linear_interp(70.0, 80.0, 0.892, 0.707, self.speed)
        # 5
        else:   # self.speed > 80
            gear_ratio = 0.707

        return gear_ratio

    def __record_car_parameter(self, timestamp):
        self.speedometer.append([timestamp, self.speed])
        self.tachometer.append([timestamp, self.enginespeed])
        self.torquemeter.append([timestamp, self.torque])

        # record car status
        self.status_record.append([timestamp, self.status])

        return

    def __get_speed_loss_from_brake(self, value):
        assert(value <= 1.0)
        speed_loss = self.speed * exp(value)/exp(1.0) \
            * 1e-3/BUS_LOAD/Vehicle.brake_scale
        return speed_loss

    def __audit_engine_speed(self):
        if self.enginespeed > self.max_engine_speed:
            self.enginespeed = self.max_engine_speed
        if self.enginespeed < self.min_engine_speed:
            self.enginespeed = self.min_engine_speed
        return

    def __no_driving_action(self):
        if self.speed == 0:
            # nothing to do with car stopped
            return

        if self.status == CarStatus.ENGINE_SHUTDOWN:
            self.speed += self.speed*(-10)*Vehicle.speed_elapsing_factor
            self.power = 0
            self.enginespeed = 0
            self.torque = 0
        else:
            road_force = (random()-0.7)

            self.speed += self.speed*road_force*Vehicle.speed_elapsing_factor
            if self.speed <= 0:
                self.speed = self.enginespeed = self.power = self.torque = 0.0
                return

            self.enginespeed = self.speed * self.__get_gear_ratio() \
                * self.speed_to_enginespeed_ratio
            self.__audit_engine_speed()
            self.power += self.power*road_force*Vehicle.power_elapsing_factor
            self.torque = self.power * 9550.0 / self.enginespeed
            self.torque = Vehicle.max_torque \
                if self.torque > Vehicle.max_torque else self.torque
        return

    def get_car_model(self):
        return self.model

    def record_gas_pedal_action(self, timestamp, value):
        if self.status != CarStatus.NORMAL:
            self.record_no_action(timestamp)
        elif self.enginespeed >= self.max_engine_speed:
            # with engine speed exceeds upper bound, no fuel provided to engine
            self.record_no_action(timestamp)
        else:
            # 1. Calcuate torque by power and engine speed
            # 2. Calculate accelerating rate by torque and gear ratio
            # 3. Update speed by accelerating rate
            # 4. Update engine speed by speed
            self.power = value * self.gas_pedal_to_power_ratio
            self.torque = self.power * 9550.0 / self.enginespeed
            self.torque = Vehicle.max_torque \
                if self.torque > Vehicle.max_torque else self.torque

            acce_power = self.torque * self.__get_gear_ratio() \
                * self.torque_to_acce_power_ratio
            acce_power = Vehicle.max_acce_power \
                if acce_power > Vehicle.max_acce_power else acce_power

            self.speed = self.speed + acce_power
            self.enginespeed = self.speed * self.__get_gear_ratio() \
                * self.speed_to_enginespeed_ratio
            self.__audit_engine_speed()
            self.accpower_record.append([timestamp, acce_power])
        return

    def record_brake_pedal_action(self, timestamp, value):
        if self.status != CarStatus.NORMAL:
            self.record_no_action(timestamp)
        else:
            speed_loss = self.__get_speed_loss_from_brake(value)
            self.speed = (self.speed-speed_loss) \
                if (self.speed > speed_loss) else 0.0
            self.enginespeed = self.speed * self.__get_gear_ratio() \
                * self.speed_to_enginespeed_ratio
            self.__audit_engine_speed()
            self.torque = self.power * 9550.0 / self.enginespeed
            self.torque = Vehicle.max_torque \
                if self.torque > Vehicle.max_torque else self.torque

            self.braking_record.append([timestamp, value])
        return

    def query_vehicle_status(self):
        return self.speed, self.enginespeed, self.torque

    def record_no_action(self, timestamp):
        self.__no_driving_action()
        return

    def drive_car(self, event_list):
        # generate regular query during driving
        rt_event_list = []
        last_query_time = -100
        query_interval = 0.01  # query vehicle status every 10ms

        for event in event_list:
            self.drive_by_event(event)

            if event.timestamp-last_query_time > query_interval:
                last_query_time = event.timestamp
                speed, enginespeed, torque = self.query_vehicle_status()
                rt_event_list.extend(generate_query_event(event.timestamp,
                                     speed, enginespeed, torque))

        return rt_event_list

    def drive_by_event(self, event: CarEvent):
        # reset timer
        if event.timestamp - self.driving_int >= 1.0:
            self.driving_int = int(event.timestamp)
            if self.status == CarStatus.DOS_DETECTED and \
               self.hpmsg < Vehicle.invalid_msg_threshold:
                # Vehicle status in 'DOS attacking' could be recovered
                self.status = CarStatus.NORMAL
            elif self.status == CarStatus.ENGINE_SHUTDOWN:
                pass
            self.hpmsg = self.rlengine = 0

        # drive the car by event fed in
        if event.ID <= 0x10:
            # detect DOS attack
            # count number of messages with high priority
            self.hpmsg += 1
            if self.status == CarStatus.NORMAL and \
               self.hpmsg >= Vehicle.invalid_msg_threshold:
                self.status = CarStatus.DOS_DETECTED
                print("Car status changed: DOS attack detected at",
                      event.timestamp)
        elif event.ID == CarEvent.CAR_EVENT_GAS_PEDAL:
            self.record_gas_pedal_action(event.timestamp, event.value)
        elif event.ID == CarEvent.CAR_EVENT_GAS_ACC_VIA_ICE:
            if event.value == 1:
                # overwrought the engine until it is killed
                self.rlengine += 1
                if self.status == CarStatus.NORMAL and \
                   self.rlengine >= Vehicle.invalid_msg_threshold:
                    self.status = CarStatus.ENGINE_SHUTDOWN
                    print("Car status changed: engine killed !",
                          event.timestamp)
        elif event.ID == CarEvent.CAR_EVENT_BRAKE_PEDAL:
            self.record_brake_pedal_action(event.timestamp, event.value)
        elif event.ID == CarEvent.CAR_EVENT_FREE:
            self.record_no_action(event.timestamp)

        # record car parameters and status
        self.__record_car_parameter(event.timestamp)

    def get_speedometer_record(self):
        return self.speedometer

    def get_tachometer_record(self):
        return self.tachometer

    def get_braking_record(self):
        return self.braking_record

    def get_torque_record(self):
        return self.torquemeter

    def get_accpower_record(self):
        return self.accpower_record


def get_event_timing_from_interval(start_second, stop_second, load_ratio):
    # generate event on random timing point between start_time
    # and stop_time, in unit of ms
    timing_interval = range(int(start_second*1e3), int(stop_second*1e3))
    event_number = int(CAN_DATA_RATE/CAN_FRAME_LEN
                       * (stop_second-start_second) * BUS_LOAD * load_ratio)
    event_number = len(timing_interval) \
        if event_number > len(timing_interval) else event_number
    timing_seq = [i*1e-3 for i in sample(timing_interval, event_number)]
    return sorted(timing_seq)


def generate_constant_event(start_time=.0, stop_time=10.0, acceleration=0):
    event_list = []

    # -----------------------------------------------------
    # create accelaration event
    acce_ratio = ACCE_RATIO
    time_seq = get_event_timing_from_interval(start_time, stop_time,
                                              acce_ratio)
    event_list.extend(
        [CarEvent(desc="Accelerating", timestamp=i,
                  ID=CarEvent.CAR_EVENT_GAS_PEDAL, value=0.95)
         for i in time_seq if acceleration > 0])

    return event_list

    # -----------------------------------------------------
    # create diagnostic event
    diag_ratio = 0.1
    time_seq = get_event_timing_from_interval(start_time, stop_time,
                                              diag_ratio)

    for i in time_seq:
        event = CarEvent(desc="Diagnostic", timestamp=i,
                         ID=CarEvent.CAR_EVENT_BUS_DIAG, value=random())
        event_list.append(event)

    return event_list


def generate_sporadic_event(start_time=.0, stop_time=10.0, brake=0):
    event_list = []

    # -----------------------------------------------------
    # create braking event
    brak_ratio = BRAK_RATIO
    time_seq = get_event_timing_from_interval(start_time, stop_time,
                                              brak_ratio)
    event_list.extend(
        [CarEvent("braking", timestamp=i,
                  ID=CarEvent.CAR_EVENT_BRAKE_PEDAL, value=0.5)
         for i in time_seq if brake > 0])

    return event_list

    braking_interval = 5.0   # braking event average interval
    while True:
        braking_start = expovariate(1.0/braking_interval)

        # Suppose a braking event lasts for 1 second
        if (braking_start + start_time + 1 >= stop_time):
            break

        # braking_value = random()
        braking_value = 0.5
        for i in time_seq:
            event = CarEvent(desc="braking", timestamp=i,
                             ID=CarEvent.CAR_EVENT_BRAKE_PEDAL,
                             value=braking_value)
            event_list.append(event)


def generate_DOS_attack_via_odbII(start_time, stop_time):

    # create attack event
    dos_ratio = DOS_RATIO
    time_seq = get_event_timing_from_interval(start_time, stop_time, dos_ratio)

    # generate invalude odb messages with ID ranging from 0 to 0x10 to
    # hold the highest prioritized position
    dos_list = [CarEvent("DOS attack", timestamp=time, ID=randint(0, 0x10),
                value=random()) for time in time_seq]
    return dos_list


def toyota_prius_force_shutdown_engine(start_time, stop_time):
    # the command applied to toyota prius, with two options:
    # 1. diagnostic tests to kill the fuel of all cylinders to ICE
    # 2. use 0x0037 CAN ID to redline the ICE and eventurally force the
    # engine to shut down
    # Note: Option 2 can permanently damage the automobile. use caution
    time_seq = get_event_timing_from_interval(start_time, stop_time, 1)
    attack_list = [
        CarEvent("Shut down engine", timestamp=time,
                 ID=CarEvent.CAR_EVENT_GAS_ACC_VIA_ICE, value=1)
        for time in time_seq]
    return attack_list


def generate_empty_event(start_time, stop_time, event_list):
    full_time = range(int(start_time*1e3), int(stop_time*1e3))
    busy_time = [event.timestamp*1e3 for event in event_list]
    free_time = set(full_time)-set(busy_time)
    free_list = [CarEvent("Free", time*1e-3, CarEvent.CAR_EVENT_FREE)
                 for time in free_time]
    return free_list


def generate_query_event(timestamp, speed, enginespeed, torque):
    query_list = []
    query_list.append(CarEvent("query speed", timestamp=timestamp,
                               ID=CarEvent.CAR_EVENT_QUERY_SPEED,
                               value=speed))
    query_list.append(CarEvent("query enginespeed", timestamp=timestamp,
                               ID=CarEvent.CAR_EVENT_QUERY_RPM,
                               value=enginespeed))
    query_list.append(CarEvent("query torque", timestamp=timestamp,
                               ID=CarEvent.CAR_EVENT_QUERY_TORQUE,
                               value=torque))
    return query_list
