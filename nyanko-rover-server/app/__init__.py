from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
#from flask_socketio import SocketIO
import logging
import os

# Module(s) that I created for this project
import NyankoRoverWebSocket
import motor_control

login_manager = LoginManager()
login_manager.login_message_category = 'info'

# View to redirect to when the login is required
login_manager.login_view = 'login'

app = Flask(__name__)
#socketio = SocketIO(app)

db = SQLAlchemy(app)

app.config['SECRET_KEY'] = os.environ['NYANKO_ROVER_SECRET_KEY']
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

db.init_app(app)

login_manager.init_app(app)

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
from app import models