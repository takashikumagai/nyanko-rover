import motor_controller
import RPi.GPIO as gpio
import logging

class MotorController_L293D(MotorController):

    # For controlling the forward/backward motor
    Motor1_Enable = 32
    Motor1_A1 = 36
    Motor1_A2 = 38

    # For controlling the steering motor (i.e. the motor for turning right or left)
    Motor2_Enable = 22
    Motor2_A1 = 24
    Motor2_A2 = 26

    def __init__(self):
        self.fwd_back_motor = None
        self.steering_motor = None

    def init_gpio(self):
        gpio.setup(self.Motor1_A1,gpio.OUT)
        gpio.setup(self.Motor1_A2,gpio.OUT)
        gpio.setup(self.Motor1_Enable,gpio.OUT)
        gpio.setup(self.Motor2_A1,gpio.OUT)
        gpio.setup(self.Motor2_A2,gpio.OUT)
        gpio.setup(self.Motor2_Enable,gpio.OUT)

        # Create a PWM instance and sets the duty cycle to 0 so that the motor will not start rotating yet.
        pwm_frequency = 50
        self.fwd_back_motor = gpio.PWM(self.Motor1_Enable,pwm_frequency)
        self.fwd_back_motor.start(0)
        self.steering_motor = gpio.PWM(self.Motor2_Enable,pwm_frequency)
        self.steering_motor.start(0)

    def cleanup_gpio(self):
        gpio.output(self.Motor1_Enable,gpio.LOW)
        gpio.output(self.Motor1_A1,gpio.LOW)
        gpio.output(self.Motor1_A2,gpio.LOW)
        gpio.output(self.Motor2_Enable,gpio.LOW)
        gpio.output(self.Motor2_A1,gpio.LOW)
        gpio.output(self.Motor2_A2,gpio.LOW)

    def set_fwd_back_motor_speed(self, speed):
        #global fwd_back_motor
        speed = clamp(speed, -100, 100)

        if 1 < speed:
            logging.debug('pwd f: {}'.format(speed))
            gpio.output(self.Motor1_A1,gpio.HIGH)
            gpio.output(self.Motor1_A2,gpio.LOW)
            self.fwd_back_motor.ChangeDutyCycle(speed)
        elif speed < -1:
            logging.debug('pwd b: {}'.format(speed))
            gpio.output(self.Motor1_A1,gpio.LOW)
            gpio.output(self.Motor1_A2,gpio.HIGH)
            self.fwd_back_motor.ChangeDutyCycle(abs(speed))
        else: # -1 <= speed <= 1
            logging.debug('pwd f/b stop: {}'.format(speed))
            self.fwd_back_motor.ChangeDutyCycle(0)

    def set_steering(self, steer):
        #global steering_motor
        steer = clamp(steer, -100.0, 100.0)

        if 1 < steer:
            logging.debug('pwd left: {}'.format(steer))
            gpio.output(self.Motor2_A1,gpio.HIGH)
            gpio.output(self.Motor2_A2,gpio.LOW)
            self.steering_motor.ChangeDutyCycle(steer)
        elif steer < -1:
            logging.debug('pwd right: {}'.format(steer))
            gpio.output(self.Motor2_A1,gpio.LOW)
            gpio.output(self.Motor2_A2,gpio.HIGH)
            self.steering_motor.ChangeDutyCycle(abs(steer))
        else: # -1 <= steer <= 1
            logging.debug('pwd l/r stop: {}'.format(steer))
            self.steering_motor.ChangeDutyCycle(0)

    def rotate_motor_cw(self):
        gpio.output(self.Motor1_A1,gpio.HIGH)
        gpio.output(self.Motor1_A2,gpio.LOW)
        #gpio.output(self.Motor1_Enable,gpio.HIGH)
        self.fwd_back_motor.ChangeDutyCycle(100)

    def rotate_motor_ccw(self):
        gpio.output(self.Motor1_A1,gpio.LOW)
        gpio.output(self.Motor1_A2,gpio.HIGH)
        #gpio.output(self.Motor1_Enable,gpio.HIGH)
        self.fwd_back_motor.ChangeDutyCycle(100)

    def stop_motor(self):
        #gpio.output(self.Motor1_Enable,gpio.LOW)
        self.fwd_back_motor.ChangeDutyCycle(0)