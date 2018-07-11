import sys
import struct
import time

from vehicle_model import Vehicle
from vehicle_model import generate_constant_event, generate_sporadic_event, generate_empty_event, generate_query_event
from vehicle_model import generate_DOS_attack_via_odbII

from packet_proc import write_car_event_to_can_packet, write_car_event_to_udp_packet
from packet_proc import read_car_event_from_udp_packet

from visulization_proc import draw_timed_sequence
from visulization_proc import visual_setup, visual_teardown
from glob_def import CarEvent

def sort_event_by_timestamp(event_list):
    def customer_key(event):
        return event.timestamp

    event_list.sort(key=customer_key)
    return

def drive_the_car(car, event_list):

    # generate regular query during driving
    rt_event_list = []
    last_query_time = -100
    query_interval = 0.01 # query vehicle status every 10ms


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
            rt_event_list.extend(generate_query_event(event.timestamp, speed, enginespeed, torque))
    
    return rt_event_list

def main():
    

    generate_car_data = 1
    analyze_car_data = 1

    dos_attack = 1

    car = Vehicle("Toyota_prius")

    if generate_car_data:
        #simulation_start = time.time()
        sim_start = 0
        sim_time = 20 # simulation time, unit of second
        event_list = []

        # generate constant events for every second
        for i in range(sim_time):        
            acceleration = 1 if i<7 or 12<=i<16  else 0
            const_event = generate_constant_event(sim_start+i, sim_start+i+1, acceleration)
            event_list.extend(const_event)

        # generate braking events only on sparodic timing points
        for i in range(sim_time):
            brake = 1 if 10<=i<11 or 17<=i<18 else 0
            sparodic_event = generate_sporadic_event(sim_start+i, sim_start+i+1, brake)
            event_list.extend(sparodic_event)

        # mark every free time point
        free_event = generate_empty_event(sim_start, sim_start+sim_time, event_list)
        event_list.extend(free_event)

        sort_event_by_timestamp(event_list)

        # generate DOS attack scenario
        if dos_attack:
            attack_start_time = 15.0
            attack_stop_time = 16.0
            attack_list = generate_DOS_attack_via_odbII(attack_start_time, attack_stop_time)
            event_list.extend(attack_list)
            sort_event_by_timestamp(event_list)

        # drive the car with preset events, and generate more real-time events
        rt_event_list = drive_the_car(car, event_list)
        event_list.extend(rt_event_list)
        sort_event_by_timestamp(event_list)

        #write_car_event_to_can_packet(car, event_list)
        write_car_event_to_udp_packet(car, event_list)

        # visualize the result
        visual_setup()

        draw_timed_sequence(car.get_speedometer_record(), "Speed [kmph]", (-10, 180))
        draw_timed_sequence(car.get_tachometer_record(), "Engine Speed [RPM]", (-10, 6000))
        draw_timed_sequence(car.get_torque_record(), "Torque [N-m]", (-10, 260))
    
        visual_teardown()
    if analyze_car_data:
        event_out = read_car_event_from_udp_packet(car)

        speed_record = [[i.timestamp, i.value] for i in event_out if i.ID == CarEvent.CAR_EVENT_QUERY_SPEED]
        rpm_record = [[i.timestamp, i.value] for i in event_out if i.ID == CarEvent.CAR_EVENT_QUERY_RPM]
        torque_record = [[i.timestamp, i.value] for i in event_out if i.ID == CarEvent.CAR_EVENT_QUERY_TORQUE]

        visual_setup()
        draw_timed_sequence(speed_record, "Retrived speed [kmph])", (-10, 180))
        draw_timed_sequence(rpm_record, "Retrived Engine Speed [RPM])", (-10, 6000))
        draw_timed_sequence(torque_record, "Retrived Torque [N-m])", (-10, 260))
        visual_teardown()

    return

if __name__ == '__main__':
    main()
