import pigpio
import logging
import socket

# Initializes and manages pigpio instances, assuming that
# - pigpiod is running
# - Environment variable PIGPIO_PORT is set to the port
#   pigpiod is running on if the port is not 8888.

class PiGPIO:

    pi = None

    @classmethod
    def init(cls):
        logging.info('Initializing pigpio.')

        #cls.pi = pigpio.pi() # Connect to local pi

        # Once pigpio.pi() on a machine via ssh caused an error
        # and hostname had to be specified. Later executions
        # of the script in the same environment did not cause the error
        # and reasons for this discrepancy was not resolved.
        cls.pi = pigpio.pi(socket.gethostname()) # Connect to local pi

    @classmethod
    def get_pi_instance(cls):
        if cls.pi is None:
            cls.init()

        return cls.pi

    @classmethod
    def release(cls):
        if cls.pi is not None:
            logging.info('Releasing pigpio resources.')
            cls.pi.stop()
            cls.pi = None