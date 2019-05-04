#!/usr/bin/env python3

from time import sleep
import logging

shtudown_requested = False

# Low-level functions

def rotate_motor_cw():
    print('🚗 Motor-CW')

def rotate_motor_ccw():
    print('🚗 Motor-CCW')

def stop_motor():
    print('🚗 Motor-STOP')

def init():
    print('🚗 Init')

def cleanup():
    print('🚗 Cleanup')


# High-level functions

# param[in] speed must be an integer in the range [-100,100]
def set_fwd_back_motor_speed(speed):
    print('🚗 fwd/back {}'.format(speed))

# param[in] steer must be an integer in the range [-100,100]
def set_steering(steer):
    print('🚗 steer {}'.format(steer))

def start_motor_forward(rotation_speed):
    rotate_motor_cw()

def start_motor_backward(rotation_speed):
    rotate_motor_ccw()

def run():
    global shtudown_requested
    while not shtudown_requested:
        sleep(0.05)

    logging.debug('Exiting motor_control.run() (stub).')

def shutdown():
    global shtudown_requested
    shtudown_requested = True
    pass

def start_thread():
    print('starting')

def join():
    print('joining')

if __name__ == '__main__':
    run()

