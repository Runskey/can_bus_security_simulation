import sys
import struct
import configparser

from vehicle_model import Vehicle
from vehicle_model import generate_constant_event, generate_sporadic_event
from vehicle_model import car_set_gear
from vehicle_model import generate_empty_event, generate_query_event
from vehicle_model import generate_DOS_attack_via_odbII
from vehicle_model import toyota_prius_force_shutdown_engine

from packet_proc import write_car_event_to_can_packet
from packet_proc import write_car_event_to_udp_packet
from packet_proc import read_car_event_from_udp_packet

from visulization_proc import draw_timed_sequence, draw_animation
from visulization_proc import visual_setup, visual_teardown
from glob_def import CarEvent, AttackModel, GearShiftStatus
from glob_def import ATTACK_TYPE_DDOS, ATTACK_TYPE_REVERSE_GAS, ATTACK_TYPE_KILL_ENGINE

from matplotlib import pyplot as mplt
from matplotlib.animation import FuncAnimation
from matplotlib import patheffects
import numpy as np


def sort_event_by_timestamp(event_list):
    def customer_key(event):
        return event.timestamp

    event_list.sort(key=customer_key)
    return


def drive_the_car(car, event_list):
    # generate regular query during driving
    rt_event_list = []
    last_query_time = -100
    query_interval = 0.01  # query vehicle status every 10ms

    for event in event_list:
        if event.ID == CarEvent.CAR_EVENT_GAS_PEDAL:
            car.record_gas_pedal_action(event.timestamp, event.value)
        elif event.ID == CarEvent.CAR_EVENT_BRAKE_PEDAL:
            car.record_brake_pedal_action(event.timestamp, event.value)
        elif event.ID == CarEvent.CAR_EVENT_FREE:
            car.record_no_action(event.timestamp)

        if event.timestamp-last_query_time > query_interval:
            last_query_time = event.timestamp
            speed, enginespeed, torque = car.query_vehicle_status()
            rt_event_list.extend(
                generate_query_event(event.timestamp, speed, enginespeed,
                                     torque))

    return rt_event_list


def read_attack_config():
    attack_list = []
    conf = configparser.ConfigParser()
    conf.read("attack_conf.txt")
    attack_scenarios = conf.sections()

    for attack in attack_scenarios:
        attack_model = AttackModel()
        type = conf.get(attack, "attack_type").lower()
        if "ddos" in type:
            attack_model.type = ATTACK_TYPE_DDOS
        elif "reverse" in type:
            attack_model.type = ATTACK_TYPE_REVERSE_GAS
        elif "kill engine" in type:
            attack_model.type = ATTACK_TYPE_KILL_ENGINE

        strength = conf.get(attack, "strength").lower()
        attack_model.strength = strength

        condition = conf.get(attack, "condition").lower()
        for subcondition in condition.split(' and '):
            if "gearshift" in subcondition:
                attack_model.is_gearshift_check = True
                if "reverse" in subcondition:
                    attack_model.gearshift = "reverse"
                elif "drive" in subcondition:
                    attack_model.gearshift = "drive"

            if "speed" in subcondition:
                attack_model.is_speed_check = True
                speed_range = subcondition.split('<')
                if len(speed_range) == 3:
                    # extract both low and high value of speed range
                    attack_model.speed_low = int(
                        speed_range[0].replace('kmph', ''))
                    attack_model.speed_high = int(
                        speed_range[2].replace('kmph', ''))
                elif len(speed_range) == 2:
                    # extract only high value of speed
                    attack_model.speed_high = int(
                        speed_range[1].replace('kmph', ''))
                else:
                    speed_range = subcondition.split('>')
                    attack_model.speed_low = int(
                        speed_range[1].replace('kmph', ''))
        attack_list.append(attack_model)
    return attack_list


def main():

    attack_list = read_attack_config()
    print(f"There are {len(attack_list)} attacks established:")
    for attack in attack_list:
        print("    ", attack)

    generate_car_data = 1
    analyze_car_data = 1
    show_animaiton = 1

    attack_dos = 0
    attack_kill_engine = 0

    car = Vehicle("Toyota_prius", speed=0.0)
    # car = Vehicle("Toyota_prius", speed=80.0)

    # Register attack model from configuration file
    car.register_attack_model(attack_list[0])

    if generate_car_data:
        # simulation_start = time.time()
        sim_start = 0
        sim_time = 20  # simulation time, unit of second
        event_list = []

        # Start the car
        event_list.extend(
            car_set_gear(sim_start, GearShiftStatus.DRIVE)
        )

        # generate constant events for every second
        for i in range(sim_time):
            acceleration = 1 if i < 7 or 12 <= i < 16 else 0
            const_event = generate_constant_event(
                sim_start+i, sim_start+i+1, acceleration)
            event_list.extend(const_event)

        # generate braking events only on sparodic timing points
        for i in range(sim_time):
            brake = 1 if (10 <= i < 11) or (17 <= i < 18) else 0
            sparodic_event = \
                generate_sporadic_event(sim_start+i, sim_start+i+1, brake)
            event_list.extend(sparodic_event)

        # mark every free time point
        free_event = \
            generate_empty_event(sim_start, sim_start+sim_time, event_list)
        event_list.extend(free_event)

        sort_event_by_timestamp(event_list)

        # generate DOS attack scenario
        if attack_dos:
            attack_start_time = 15.0
            attack_stop_time = 16.0
            attack_list = \
                generate_DOS_attack_via_odbII(attack_start_time,
                                              attack_stop_time)
            event_list.extend(attack_list)
            sort_event_by_timestamp(event_list)

        if attack_kill_engine and car.get_car_model() == "Toyota_prius":
            attack_start_time = 16.0
            attack_stop_time = 17.0
            attack_list = \
                toyota_prius_force_shutdown_engine(attack_start_time,
                                                   attack_stop_time)
            event_list.extend(attack_list)
            sort_event_by_timestamp(event_list)

        # drive the car with preset events, and generate more real-time events
        rt_event_list = car.drive_car(event_list)
        # rt_event_list = drive_the_car(car, event_list)
        event_list.extend(rt_event_list)
        sort_event_by_timestamp(event_list)

        write_car_event_to_udp_packet(car, event_list)

        # visualize the result
        visual_setup()
    # draw_timed_sequence(car.get_speedometer_record(), "Speed [kmph]", (-10, 180))
    # draw_timed_sequence(car.get_tachometer_record(), "Engine Speed [RPM]", (-10, 6000))
    # draw_timed_sequence(car.get_torque_record(), "Torque [N-m]", (-10, 260))
        visual_teardown()

    if analyze_car_data:
        event_out = read_car_event_from_udp_packet(car)

        speed_record = [[i.timestamp, i.value] for i in event_out
                        if i.ID == CarEvent.CAR_EVENT_QUERY_SPEED]
        rpm_record = [[i.timestamp, i.value] for i in event_out
                      if i.ID == CarEvent.CAR_EVENT_QUERY_RPM]
        torque_record = [[i.timestamp, i.value] for i in event_out
                         if i.ID == CarEvent.CAR_EVENT_QUERY_TORQUE]

        visual_setup()
        draw_timed_sequence(speed_record, "Retrived speed [kmph])", (-10, 180))
        # draw_timed_sequence(rpm_record, "Retrived Engine Speed [RPM])", (-10, 6000))
        # draw_timed_sequence(torque_record, "Retrived Torque [N-m])", (-10, 260))

        '''
        show animaiton of observed parameters
        '''
        if show_animaiton:
            data_src = (speed_record, rpm_record, torque_record)
            line_ani = draw_animation(data_src)

        visual_teardown()

    return


if __name__ == '__main__':
    main()
