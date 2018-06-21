import sys
import struct
import time

from vehicle_model import Vehicle, generate_constant_event, generate_sporadic_event, calculate_vehicle_speed
from packet_proc import write_can_packet
from visulization_proc import draw_speedometer, gauge
from glob_def import *

def sort_event_by_timestamp(event_list):
    def customer_key(event):
        return event.timestamp

    event_list.sort(key=customer_key)
    return

def drive_the_car(car, event_list):
    for event in event_list:
        if event.ID == CAN_ID_ACCE:
            car.record_gas_pedal_action(event.timestamp, event.value)
        elif event.ID == CAN_ID_BRAK:
            car.record_brake_pedal_action(event.timestamp, event.value)
    
    return

def main():
    
    #simulation_start = time.time()
    simulation_start = 0
    simulation_time = 15 # simulation time, unit of second
    event_list = []
    car = Vehicle("Toyota_prius")

    # generate constant events for every second
    for i in range(simulation_time):
        acceleration = 1
        const_event = generate_constant_event(simulation_start+i, simulation_start+i+1, acceleration)
        event_list.extend(const_event)

    # generate braking events only on sparodic timing points
    sparodic_event = generate_sporadic_event(simulation_start, simulation_start+simulation_time)
    event_list.extend(sparodic_event)

    sort_event_by_timestamp(event_list)

    car = Vehicle("test car")
    drive_the_car(car, event_list)

    speed_list = car.get_speedometer_record()

    write_can_packet(car, event_list)

    # plot the result
    draw_speedometer(speed_list)

    return


if __name__ == '__main__':
    main()
