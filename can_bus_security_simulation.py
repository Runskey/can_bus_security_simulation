import sys
import struct
import time

from vehicle_model import Vehicle, generate_constant_event, generate_sporadic_event, generate_empty_event
from packet_proc import write_can_packet
from visulization_proc import draw_timed_sequence
from visulization_proc import visual_setup, visual_teardown
from glob_def import CarEvent

def sort_event_by_timestamp(event_list):
    def customer_key(event):
        return event.timestamp

    event_list.sort(key=customer_key)
    return

def drive_the_car(car, event_list):
    for event in event_list:
        if event.ID == CarEvent.CAR_EVENT_GAS_PEDAL:
            car.record_gas_pedal_action(event.timestamp, event.value)
        elif event.ID == CarEvent.CAR_EVENT_BRAKE_PEDAL:
            car.record_brake_pedal_action(event.timestamp, event.value)
        elif event.ID == CarEvent.CAR_EVENT_FREE:
            car.record_no_action(event.timestamp)
    
    return

def main():
    
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

    car = Vehicle("Toyota_prius")
    drive_the_car(car, event_list)

    # write_can_packet(car, event_list)

    # visualize the result
    visual_setup()

    draw_timed_sequence(car.get_speedometer_record(), "Speed [kmph])", (-10, 180))
    draw_timed_sequence(car.get_tachometer_record(), "Engine Speed [RPM]", (-10, 6000))
    draw_timed_sequence(car.get_torque_record(), "Torque [N-m]", (-10, 260))

    #draw_speedometer(speed_list)
    #draw_tachometer(tach_list)
    #draw_torque_curve(torque_list)
    #draw_acc_curve(accpwr_list)
    
    visual_teardown()

    return

if __name__ == '__main__':
    main()
