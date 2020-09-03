#!/usr/bin/env python3

from time import sleep
import logging
import threading
import queue
#import motor_controller_L293D
import motor_controller_TEU_105BK

myqueue = None
shutdown_requested = False
motor_controller_thread = None

def clamp(my_value, min_value, max_value):
    return max(min(my_value, max_value), min_value)

# speed: [-100,100], where -100 is backward at full speed and 100 is forward at full speed

def init_gpio():
    global motor_controller
    logging.info('Initializing GPIO.')
    #gpio.cleanup()
    #gpio.setmode(gpio.BOARD)
    motor_controller.init_gpio()

def cleanup():
    global motor_controller
    logging.info('Cleaning up GPIO pins.')
    motor_controller.cleanup_gpio()
    #gpio.cleanup()

def mainloop():
    global motor_controller
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
                motor_controller.rotate_motor_cw()
            elif code == 'b':
                motor_controller.rotate_motor_ccw()
            elif code == 'h':
                motor_controller.stop_motor()
        elif 1 < len(item):
            value = int(item[1:])
            logging.debug('item value: {}'.format(value))
            if code == 'f':
                motor_controller.set_fwd_back_motor_speed(value)
            elif code == 's':
                motor_controller.set_steering(value)
        else:
            logging.error('unexpected item format: {}'.format(item))

    # Exited the main loop because the shutdown was requested; stop the motors before terminating the thread
    motor_controller.stop_motor()
    # return_sterring_motor_to_neutral()

# High-level functions

def start_motor_forward(rotation_speed):
    global motor_controller
    motor_controller.rotate_motor_cw()

def start_motor_backward(rotation_speed):
    global motor_controller
    motor_controller.rotate_motor_ccw()

### Public APIs ###

# May be called by a separate thread but must be called before the motor_control thread is started.
def init():
    global myqueue
    global motor_controller

    logging.info('Initializing request queue and motor controller')

    myqueue = queue.Queue()

    #motor_controller = motor_controller_L293D.MotorController_L293D()
    motor_controller = motor_controller_TEU_105BK.MotorController_TEU105BK()

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
    logging.info('Setting up the motor controller thread...')
    init()
    motor_controller_thread = threading.Thread(target = run)
    motor_controller_thread.start()

def join():
    global motor_controller_thread
    if motor_controller_thread is not None:
        motor_controller_thread.join()
    else:
        logging.info('!motor_controller_thread')

if __name__ == '__main__':
    logging.info('init and run')
    init()
    run()
