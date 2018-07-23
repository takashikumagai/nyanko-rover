#!/usr/bin/env python3

from time import sleep
import logging

shtudown_requested = False

# Low-level functions

def rotate_motor_cw():
    pass

def rotate_motor_ccw():
    pass

def stop_motor():
    pass

def init():
    pass

def cleanup():
    pass


# High-level functions
def set_fwd_back_motor_speed(speed):
    print('fwd/back {}'.format(speed))
    pass

def start_motor_forward(rotation_speed):
    rotate_motor_cw()

def start_motor_backward(rotation_speed):
    rotate_motor_ccw()

def run():
    global shtudown_requested
    while not shtudown_requested:
        pass
    logging.debug('Exiting motor_control.run() (stub).')

def shutdown():
    global shtudown_requested
    shtudown_requested = True
    pass

if __name__ == '__main__':
    run()

