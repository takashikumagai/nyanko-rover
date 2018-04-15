#!/usr/bin/env python3

import RPi.GPIO as gpio
from time import sleep
import logging
import queue

# For controlling the forward/backward motor
Motor1_Enable = 32
Motor1_A1 = 36
Motor1_A2 = 38

fwd_back_motor = None

# For controlling the steering motor (i.e. the motor for turning right or left)
#Motor2_Enable = 
#Motor2_A1 = 
#Motor2_A2 = 

myqueue = None
shutdown_requested = False

def clamp(my_value, min_value, max_value):
    return max(min(my_value, max_value), min_value)

# speed: [-100,100], where -100 is backward at full speed and 100 is forward at full speed
def do_set_fwd_back_motor_speed(speed):
    speed = clamp(speed, -100.0, 100.0)

    if 1.0 < speed:
        print('pwd f: {}'.format(speed))
        gpio.output(Motor1_A1,gpio.HIGH)
        gpio.output(Motor1_A2,gpio.LOW)
        fwd_back_motor.ChangeDutyCycle(speed)
    elif speed < -1.0:
        print('pwd b: {}'.format(speed))
        gpio.output(Motor1_A1,gpio.LOW)
        gpio.output(Motor1_A2,gpio.HIGH)
        fwd_back_motor.ChangeDutyCycle(abs(speed))
    else: # -1.0 <= speed <= 1.0
        print('pwd f/b stop: {}'.format(speed))
        fwd_back_motor.ChangeDutyCycle(0)

def do_set_steering(steer):
    steer = clamp(steer, -100.0, 100.0)

def do_rotate_motor_cw():
    gpio.output(Motor1_A1,gpio.HIGH)
    gpio.output(Motor1_A2,gpio.LOW)
    gpio.output(Motor1_Enable,gpio.HIGH)

def do_rotate_motor_ccw():
    gpio.output(Motor1_A1,gpio.LOW)
    gpio.output(Motor1_A2,gpio.HIGH)
    gpio.output(Motor1_Enable,gpio.HIGH)

def do_stop_motor():
    gpio.output(Motor1_Enable,gpio.LOW)

def init_gpio():
    logging.info('Initializing GPIO.')
    gpio.cleanup()
    gpio.setmode(gpio.BOARD)
    gpio.setup(Motor1_A1,gpio.OUT)
    gpio.setup(Motor1_A2,gpio.OUT)
    gpio.setup(Motor1_Enable,gpio.OUT)

    # Create a PWM instance and sets the duty cycle to 0 so that the motor will not start rotating yet.
    pwm_frequency = 50
    fwd_back_motor = gpio.PWM(Motor1_Enable,pwm_frequency)
    fwd_back_motor.start(0)

def cleanup():
    gpio.output(Motor1_Enable,gpio.LOW)
    gpio.output(Motor1_A1,gpio.LOW)
    gpio.output(Motor1_A2,gpio.LOW)
    gpio.cleanup()

def mainloop():
    logging.info('entering the main loop.')
    while shutdown_requested == False:

        global myqueue
        item = myqueue.get(block = True)
        if item is None:
            continue
        
        code = item[0:1]
        if len(item) == 1:
            if code == 'f':
                do_rotate_motor_cw()
            elif code == 'b':
                do_rotate_motor_ccw()
            elif code == 'h':
                do_stop_motor()
        elif 1 < len(item):
            value = int(item[1:])
            if code == 'f':
                do_set_fwd_back_motor_speed(value)
            elif code == 's':
                do_set_steering(value)
        else:
            logging.error('unexpected item format: {}'.format(item))

    # Exited the main loop because the shutdown was requested; stop the motors before terminating the thread
    do_stop_motor()
    # return_sterring_motor_to_neutral()

# High-level functions

def start_motor_forward(rotation_speed):
    rotate_motor_cw()

def start_motor_backward(rotation_speed):
    rotate_motor_ccw()

### Public APIs ###

# May be called by a separate thread but must be called before the motor_control thread is started.
def init():
    global myqueue
    myqueue = queue.Queue()
   

# These APIs put an item on a queue and return control to the caller immediately

def rotate_motor_cw():
    myqueue.put('f')

def rotate_motor_ccw():
    myqueue.put('b')

def stop_motor():
    myqueue.put('h')

def set_fwd_back_motor_speed(speed):
    myqueue.put('f{}'.format(speed))

def set_steering(steer):
    myqueue.put('s{}'.format(speed))

def shutdown():
    shutdown_requested = True

# Precondition: init() has been called and all the init calls were successful.
def run():

    init_gpio()

    mainloop()

    cleanup()

if __name__ == '__main__':
    init()
    run()
