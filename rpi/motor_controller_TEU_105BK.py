import motor_controller
import pigpio
import logging
import time

def clamp(my_value, min_value, max_value):
    return max(min(my_value, max_value), min_value)

# Ref: https://gist.github.com/fengye/354b5fbde72a75d74c5115856c797e2e#file-tamiya-finespec-2-4g-drive-protocol-L3

class MotorController_TEU105BK(motor_controller.MotorController):

    steering_servo_pin = 11
    motor_control_pin = 12
    pwm_frequency = 57.67

    # From the gist above (1000us = 1ms), duty cycles for each motor state are
    # - neutral: 1.5 / 17.34 = 0.08650519031141869 => 8.650519%
    # - maximum fwd speed: 1.1 / 17.34 = 0.06343713956170705 => 6.343714%
    # - maximum backward speed: 1.9 / 17.34 = 0.10957324106113032 => 10.957324%
    max_fwd_speed_duty_cycle = 6.343714
    max_back_speed_duty_cycle = 10.957324
    #dc_motor_neutral = 7.8 #8.4 #8.65
    #dc_motor_fwd = 7.2 #7.8 #7.20
    #dc_motor_back = 8.4 #8.7 #9.80

    # 80 Hz
    #dc_motor_neutral = 12.5
    #dc_motor_fwd = 11.0
    #dc_motor_back = 14.0

    # 100 Hz
    dc_motor_neutral = 15.0
    dc_motor_fwd = 13.0
    dc_motor_back = 17.0

    dc_servo_neutral = 7.5
    dc_servo_right = 5.5
    dc_servo_left = 9.5

    def __init__(self):
        self.pi = None

    def init_gpio(self):
        self.pi = pigpio.pi() # Connect to local pi

        # Servo
        self.pi.set_PWM_range(17, 1000) # Set the range of duty cycle to [0,1000]
        self.pi.set_PWM_frequency(17, 50) # frequency in Hz
        self.pi.set_PWM_dutycycle(17, int(self.dc_servo_neutral * 10))

        # Motor
        #self.pi.set_servo_pulsewidth(18, 57.67)
        self.pi.set_PWM_range(18, 1000) # Set the range of duty cycle to [0,1000]
        self.pi.set_PWM_frequency(18, 100)
        self.pi.set_PWM_dutycycle(18, int(self.dc_motor_neutral * 10))

    def cleanup_gpio(self):
        logging.debug('Setting duty cycle to 0')
        self.pi.set_PWM_dutycycle(17, 0)
        self.pi.set_PWM_dutycycle(18, 0)

    def set_fwd_back_motor_speed(self, speed):
        speed = clamp(speed, -100, 100)

        dc = 0
        if 1 < speed:
            f = (100 - speed) * 0.01 # Convert speed to an intermediate value of [0.0, 0.99), where 0.0 represents the max fwd speed
            dc = self.dc_motor_fwd + (self.dc_motor_neutral - self.dc_motor_fwd) * f
            logging.debug(f'fwd: {speed}, dc: {dc}')
        elif speed < -1:
            f = -speed * 0.01 # Convert speed to an intermediate value of (0.01, 1.0]
            dc = self.dc_motor_neutral + (self.dc_motor_back - self.dc_motor_neutral) * f
            logging.debug(f'fwd: {speed}, dc: {dc}')
        else: # -1 <= speed <= 1
            logging.debug(f'stopping the motor: {speed}')
            dc = self.dc_motor_neutral

        self.pi.set_PWM_dutycycle(18, int(dc * 10))

    # Steering positions and duty cycles 
    # Center: 8.0
    # Rightmost: 6.1
    # Leftmost: 9.9
    def set_steering(self, steer):
        steer = clamp(steer, -100.0, 100.0)

        dc = steer * 0.02 + self.dc_servo_neutral
        logging.debug(f'steering. dc: {dc}')
        #self.servo.ChangeDutyCycle(dc)
        self.pi.set_PWM_dutycycle(17, int(dc * 10))

    def rotate_motor_cw(self):
        logging.debug(f'operating the motor cw. dc: {self.dc_motor_fwd}')
        self.pi.set_PWM_dutycycle(18, int(self.dc_motor_fwd * 10))

    def rotate_motor_ccw(self):
        logging.debug(f'operating the motor ccw. dc: {self.dc_motor_back}')
        self.pi.set_PWM_dutycycle(18, int(self.dc_motor_back * 10))

    def stop_motor(self):
        logging.debug(f'stopping the motor. dc: {self.dc_motor_neutral}')
        self.pi.set_PWM_dutycycle(18, int(self.dc_motor_neutral * 10))

    def steer_right(self):
        dc = self.dc_servo_right
        logging.debug(f'steering right. dc: {dc}')
        self.pi.set_PWM_dutycycle(17, int(dc * 10))

    def steer_left(self):
        dc = self.dc_servo_left
        logging.debug(f'steering left. dc: {dc}')
        self.pi.set_PWM_dutycycle(17, int(dc * 10))
