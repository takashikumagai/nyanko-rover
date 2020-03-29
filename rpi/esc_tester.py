#!/usr/bin/env python3

#import RPi.GPIO as gpio
import pigpio
import logging
import sys
from time import sleep
import motor_controller_TEU_105BK

def clamp(my_value, min_value, max_value):
    return max(min(my_value, max_value), min_value)

def init_logger():
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    root.addHandler(handler)

class ESC_Tester:

    def __init__(self):
        self.motor_controller = motor_controller_TEU_105BK.MotorController_TEU105BK()
        self.init_motor_controller()

        # 0: neutral
        # -100: right
        # 100: left
        self.steering = 0

        # 0: neutral
        # 100: forward at a maximum speed
        # -100: back
        self.fwd = 0

    def init_motor_controller(self):
        #gpio.cleanup()
        #gpio.setmode(gpio.BOARD)
        self.motor_controller.init_gpio()

    def update_steering(self):
        self.motor_controller.set_steering(self.steering)

    def update_speed(self):
        self.motor_controller.set_fwd_back_motor_speed(self.fwd)

    def run(self):
        while(True):
            s = input('# ')
            if s == 'h':
                print('[Steering]')
                print('A/D: turn left/right all the way')
                print('Z/C: turn left/right by a small unit at a time')
                print('X: neutral')
                print('[Forward/Backward]')
            elif s == 'i':
                self.fwd += 5
                self.fwd = clamp(self.fwd, -100, 100)
                self.update_speed()
            elif s == 'm':
                self.fwd -= 5
                self.fwd = clamp(self.fwd, -100, 100)
                self.update_speed()
            elif s == 'k':
                self.fwd = 0
                self.update_speed()
            elif s == 'u':
                self.fwd = 100
                self.update_speed()
            elif s == 'n':
                self.fwd = -100
                self.update_speed()
            elif s == 'a':
                self.steering = 100
                #self.update_steering()
                self.motor_controller.steer_left()
            elif s == 'd':
                self.steering = -100
                #self.update_steering()
                self.motor_controller.steer_right()
            elif s == 'z':
                self.steering += 10
                self.steering = clamp(self.steering, -100, 100)
                self.update_steering()
            elif s == 'c':
                self.steering += -10
                self.steering = clamp(self.steering, -100, 100)
                self.update_steering()
            elif s == 'x':
                self.steering = 0
                self.update_steering()
            elif s == 'q':
                self.motor_controller.cleanup_gpio()

    def cleanup(self):
        self.motor_controller.cleanup_gpio()

init_logger()
esc_tester = None
try:
    esc_tester = ESC_Tester()
    esc_tester.run()
except Exception as e:
    print(f'An exception occurred: {e}')
finally:
    if esc_tester is not None:
        esc_tester.cleanup()