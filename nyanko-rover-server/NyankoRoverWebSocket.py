# Be sure to install this by 'pipenv install SimpleWebSocketServer'
# Ref: https://github.com/dpallot/simple-websocket-server
from SimpleWebSocketServer import SimpleWebSocketServer, WebSocket

import threading
import logging

class NyankoRoverWebSocket(WebSocket):

    def __init__(self):
        logging.debug("NyankoRoverWebSocket is initializing...")
    #    super(NyankoRoverWebSocket,self).__init__()
    #     WebSocket.__init__(self)
        #self.network_status_reporter = None

    def handleMessage(self):
        logging.debug("ws:message received: {}".format(self.data))

        # Unpack the data
        motor = self.data[0:1] # 'f' fwd/back or 's' for steering
        value = int(float(self.data[1:]))
        logging.debug('motor: {}, speed/steer: {}'.format(motor,value))
        if motor == 'f':
            motor_control.set_fwd_back_motor_speed(value)
        elif motor == 's':
            motor_control.set_steering(value)

    def handleConnected(self):
        logging.debug(self.address, 'ws:connected')

        self.network_status_reporter = NetworkStatusReporter.NetworkStatusReporter(self)
        self.network_status_reporter.start()

    def handleClose(self):
        logging.debug(self.address, 'ws:closed')

        if self.network_status_reporter != None:
            self.network_status_reporter.stop()

# Set up and start the WebSocket server
def create_and_start_web_socket_server(ws_port):
    logging.info('Setting up the WebSocket server...')
    ws_port = 9792
    ws_server = SimpleWebSocketServer('', ws_port, NyankoRoverWebSocket)
    logging.debug("Starting a WebSocket server (port: {}).".format(ws_port))
    websocket_server_thread = threading.Thread(target = ws_server.serveforever)
    websocket_server_thread.start()
