from PiGPIO import PiGPIO
import pigpio
import logging

class Headlamp:

    def __init__(self, pin = 26):
        self.pi = PiGPIO.get_pi_instance()
        self.brightness = 0.0
        self.pin = pin

        # PWM settings
        freq = self.pi.set_PWM_frequency(self.pin, 100)
        logging.info(f'Headlamp PWM frequency set to {freq}')

        self.pi.set_PWM_dutycycle(self.pin, 0)

    # brightness: [0.0, 1.0]
    def set_brightness(self, brightness):

        if self.pi is None:
            logging.warning('Headlamp !self.pi')
            return

        # Clamp to [0,0, 1.0]
        value = max(0.0, min(1.0, brightness))

        self.brightness = value

        dc = int(value * 255.0)
        logging.info(f'Setting headlamp PWM duty cycle to {dc}')
        self.pi.set_PWM_dutycycle(self.pin, dc)