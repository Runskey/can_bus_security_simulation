import sys
import struct
import time

import matplotlib.pyplot as mplt

from vehicle_model import constant_event, sporadic_event, calculate_vehicle_speed
from packet_proc import write_can_packet
from glob_def import CanEvent

def sort_event_by_timestamp(event_list):
    def customer_key(event):
        return event.timestamp

    event_list.sort(key=customer_key)
    return

def main():
    
    simulation_start = time.time()
    simulation_time = 10 # simulation time, unit of second
    event_list = []

    # generate constant events for every second
    for i in range(simulation_time):
        acceleration = 1 if i<5 else 0
        const_event = constant_event(simulation_start+i, simulation_start+i+1, acceleration)
        event_list.extend(const_event)

    # generate braking events only on sparodic timing points
    sparodic_event = sporadic_event(simulation_start, simulation_start+simulation_time)
    event_list.extend(sparodic_event)

    sort_event_by_timestamp(event_list)

    speed_list = calculate_vehicle_speed(simulation_start, simulation_start+simulation_time, event_list)
    
    # plot the result
    time_seq = [i.timestamp for i in event_list]
    mplt.plot(time_seq)
    mplt.show()
    return

    write_can_packet(event_list)



if __name__ == '__main__':
    main()
