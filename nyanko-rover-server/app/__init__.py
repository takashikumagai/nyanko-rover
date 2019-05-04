from flask import Flask
#from flask_socketio import SocketIO
import logging

# Module(s) that I created for this project
import NyankoRoverWebSocket
import motor_control


app = Flask(__name__)
#socketio = SocketIO(app)

if __name__ == '__main__':
    print('name:main')
    #print('Starting Flask-SocketIO')
    #socketio.run(app)

def initialize():
    log_format = '%(asctime)-15s %(thread)d %(message)s'
    logging.basicConfig(filename='nyankoroverserver.log', level=logging.DEBUG, format=log_format)
    logging.info('Nyanko Rover is starting...')

    # Start the web socket server
    NyankoRoverWebSocket.create_and_start_web_socket_server(9792)

    # Start the motor control service
    motor_control.start_thread()

# Initialize the nyanko rover server
initialize()


from app import routes
