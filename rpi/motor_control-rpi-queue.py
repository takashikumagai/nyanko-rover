#!/usr/bin/env python3

import RPi.GPIO as gpio
from time import sleep
import logging
import threading
import queue

# For controlling the forward/backward motor
Motor1_Enable = 32
Motor1_A1 = 36
Motor1_A2 = 38

# For controlling the steering motor (i.e. the motor for turning right or left)
Motor2_Enable = 22
Motor2_A1 = 24
Motor2_A2 = 26

fwd_back_motor = None
steering_motor = None

myqueue = None
shutdown_requested = False
motor_controller_thread = None

def clamp(my_value, min_value, max_value):
    return max(min(my_value, max_value), min_value)

# speed: [-100,100], where -100 is backward at full speed and 100 is forward at full speed
def do_set_fwd_back_motor_speed(speed):
    global fwd_back_motor
    speed = clamp(speed, -100, 100)

    if 1 < speed:
        logging.debug('pwd f: {}'.format(speed))
        gpio.output(Motor1_A1,gpio.HIGH)
        gpio.output(Motor1_A2,gpio.LOW)
        fwd_back_motor.ChangeDutyCycle(speed)
    elif speed < -1:
        logging.debug('pwd b: {}'.format(speed))
        gpio.output(Motor1_A1,gpio.LOW)
        gpio.output(Motor1_A2,gpio.HIGH)
        fwd_back_motor.ChangeDutyCycle(abs(speed))
    else: # -1 <= speed <= 1
        logging.debug('pwd f/b stop: {}'.format(speed))
        fwd_back_motor.ChangeDutyCycle(0)

def do_set_steering(steer):
    global steering_motor
    steer = clamp(steer, -100.0, 100.0)

    if 1 < steer:
        logging.debug('pwd left: {}'.format(steer))
        gpio.output(Motor2_A1,gpio.HIGH)
        gpio.output(Motor2_A2,gpio.LOW)
        steering_motor.ChangeDutyCycle(steer)
    elif steer < -1:
        logging.debug('pwd right: {}'.format(steer))
        gpio.output(Motor2_A1,gpio.LOW)
        gpio.output(Motor2_A2,gpio.HIGH)
        steering_motor.ChangeDutyCycle(abs(steer))
    else: # -1 <= steer <= 1
        logging.debug('pwd l/r stop: {}'.format(steer))
        steering_motor.ChangeDutyCycle(0)

def do_rotate_motor_cw():
    gpio.output(Motor1_A1,gpio.HIGH)
    gpio.output(Motor1_A2,gpio.LOW)
    #gpio.output(Motor1_Enable,gpio.HIGH)
    fwd_back_motor.ChangeDutyCycle(100)

def do_rotate_motor_ccw():
    gpio.output(Motor1_A1,gpio.LOW)
    gpio.output(Motor1_A2,gpio.HIGH)
    #gpio.output(Motor1_Enable,gpio.HIGH)
    fwd_back_motor.ChangeDutyCycle(100)

def do_stop_motor():
    #gpio.output(Motor1_Enable,gpio.LOW)
    fwd_back_motor.ChangeDutyCycle(0)

def init_gpio():
    global fwd_back_motor
    global steering_motor
    logging.info('Initializing GPIO.')
    gpio.cleanup()
    gpio.setmode(gpio.BOARD)
    gpio.setup(Motor1_A1,gpio.OUT)
    gpio.setup(Motor1_A2,gpio.OUT)
    gpio.setup(Motor1_Enable,gpio.OUT)
    gpio.setup(Motor2_A1,gpio.OUT)
    gpio.setup(Motor2_A2,gpio.OUT)
    gpio.setup(Motor2_Enable,gpio.OUT)

    # Create a PWM instance and sets the duty cycle to 0 so that the motor will not start rotating yet.
    pwm_frequency = 50
    fwd_back_motor = gpio.PWM(Motor1_Enable,pwm_frequency)
    fwd_back_motor.start(0)
    steering_motor = gpio.PWM(Motor2_Enable,pwm_frequency)
    steering_motor.start(0)

def cleanup():
    logging.info('Cleaning up GPIO pins.')
    gpio.output(Motor1_Enable,gpio.LOW)
    gpio.output(Motor1_A1,gpio.LOW)
    gpio.output(Motor1_A2,gpio.LOW)
    gpio.output(Motor2_Enable,gpio.LOW)
    gpio.output(Motor2_A1,gpio.LOW)
    gpio.output(Motor2_A2,gpio.LOW)
    gpio.cleanup()

def mainloop():
    logging.info('entering the main loop.')
    while shutdown_requested == False:

        global myqueue
        item = myqueue.get(block = True)
        if item is None:
            continue

        #logging.debug('myqueue item: {}'.format(item))
        
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
            logging.debug('item value: {}'.format(value))
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

# param[in] speed must be an integer in the range [-100,100]
def set_fwd_back_motor_speed(speed):
    #logging.debug('f/b speed: {}'.format(speed))
    myqueue.put('f{}'.format(speed))

# param[in] steer must be an integer in the range [-100,100]
def set_steering(steer):
    myqueue.put('s{}'.format(steer))

def shutdown():
    shutdown_requested = True

# Precondition: init() has been called and all the init calls were successful.
def run():

    try:
        init_gpio()
        
        mainloop()

        cleanup()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        logging.error('An exception occurred: {}'.format(str(e)))
    finally:
        logging.error('motor_control is closing.')

def start_thread():
    global motor_controller_thread
    logging.info('Setting up the motor controller...')
    init()
    motor_controller_thread = threading.Thread(target = run)
    motor_controller_thread.start()

def join():
    global motor_controller_thread
    if motor_controller_thread not None:
        motor_controller_thread.join()
    else:
        logging.info('!motor_controller_thread')

if __name__ == '__main__':
    init()
    run()
