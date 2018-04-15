#!/usr/bin/env python3

import RPi.GPIO as gpio
from time import sleep
import logging

# Low-level functions

Motor1_Enable = 32
Motor1_A1 = 36
Motor1_A2 = 38

fwd_back_motor = None

def clamp(my_value, min_value, max_value):
    return max(min(my_value, max_value), min_value)

# speed: [-100,100], where -100 is backward at full speed and 100 is forward at full speed
def set_fwd_back_motor_speed(speed):
    speed = clamp(speed, -100.0, 100.0)

    if 1.0 < speed:
        print('pwd f: {}'.format(speed))
        #gpio.output(Motor1_A1,gpio.HIGH)
        #gpio.output(Motor1_A2,gpio.LOW)
        #fwd_back_motor.ChangeDutyCycle(speed)
    elif speed < -1.0:
        print('pwd b: {}'.format(speed))
        #gpio.output(Motor1_A1,gpio.LOW)
        #gpio.output(Motor1_A2,gpio.HIGH)
        #fwd_back_motor.ChangeDutyCycle(abs(speed))
    else: # -1.0 <= speed <= 1.0
        print('pwd f/b stop: {}'.format(speed))
        #fwd_back_motor.ChangeDutyCycle(0)
        
def set_steering(steer):
    steer = clamp(steer, -100.0, 100.0)

def rotate_motor_cw():
    with open('rotate_motor_cw-called', 'w') as outputfile:
        pass
    gpio.output(Motor1_A1,gpio.HIGH)
    gpio.output(Motor1_A2,gpio.LOW)
    gpio.output(Motor1_Enable,gpio.HIGH)

def rotate_motor_ccw():
    with open('rotate_motor_ccw-called', 'w') as outputfile:
        pass
    gpio.output(Motor1_A1,gpio.LOW)
    gpio.output(Motor1_A2,gpio.HIGH)
    gpio.output(Motor1_Enable,gpio.HIGH)

def stop_motor():
    gpio.output(Motor1_Enable,gpio.LOW)

def init():
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
    stop_motor()
    gpio.output(Motor1_A1,gpio.LOW)
    gpio.output(Motor1_A2,gpio.LOW)
    gpio.cleanup()



# High-level functions

def start_motor_forward(rotation_speed):
    rotate_motor_cw()

def start_motor_backward(rotation_speed):
    rotate_motor_ccw()

def run():
    while True:
        pass

if __name__ == '__main__':
    run()
