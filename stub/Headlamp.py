import logging

class Headlamp:

    def __init__(self, pin = 26):
        self.brightness = 0.0
        self.pin = pin

        # PWM settings
        freq = 100
        logging.info(f'Headlamp PWM frequency set to {freq}')

    # brightness: [0.0, 1.0]
    def set_brightness(self, brightness):

        # Clamp to [0,0, 1.0]
        value = max(0.0, min(1.0, brightness))

        self.brightness = value

        dc = int(value * 255.0)
        logging.info(f'Setting headlamp PWM duty cycle to {dc}')
