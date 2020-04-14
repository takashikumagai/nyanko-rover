# Be sure to install this by 'pipenv install SimpleWebSocketServer'
# Ref: https://github.com/dpallot/simple-websocket-server
from SimpleWebSocketServer import SimpleWebSocketServer, WebSocket

import threading
import logging

import motor_control
#import HWStatusReporter
import NetworkStatusReporter

ws_server = None
#clients = []

#network_status_reporter = None

class NyankoRoverWebSocket(WebSocket):

# This simple ctor which just calls the super class ctor causes an error but couldn't figure out what's wrong with it.
#    def __init__(self):
#        super().__init__() # https://stackoverflow.com/questions/2399307/how-to-invoke-the-super-constructor

    # This matches with the args of WebSocket's ctor
    # Ref: https://github.com/dpallot/simple-websocket-server/blob/master/SimpleWebSocketServer/SimpleWebSocketServer.py
    def __init__(self, server, sock, address):
        super().__init__(server, sock, address)
        logging.debug("NyankoRoverWebSocket is initializing...")
#        self.hw_status_reporter = HWStatusReporter()
#    #    super(NyankoRoverWebSocket,self).__init__()
#    #     WebSocket.__init__(self)
        self.network_status_reporter = None

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
        #logging.debug(self.address, 'ws:connected')
        logging.debug('ws:connected')

        self.network_status_reporter = NetworkStatusReporter.NetworkStatusReporter(self)
        self.network_status_reporter.start()

        # hw_status = self.hw_status_reporter.get_status()

        #clients.append(self)

    def handleClose(self):
        logging.debug('ws:closed')
        #logging.debug(self.address, 'ws:closed')

        #clients.remove(self)

        #if self.network_status_reporter != None:
        #    self.network_status_reporter.stop()

# Set up and start the WebSocket server
def create_and_start_web_socket_server(ws_port):
    global ws_server
    logging.info('Setting up the WebSocket server...')
    ws_port = 9792
    try:
        ws_server = SimpleWebSocketServer('', ws_port, NyankoRoverWebSocket)
        logging.debug("Starting a WebSocket server (port: {}).".format(ws_port))
        websocket_server_thread = threading.Thread(target = ws_server.serveforever)
        websocket_server_thread.start()
    except:
        logging.error('websocket exception:', sys.exc_info()[0])


# Part of the code was taken from here:
# https://github.com/dpallot/simple-websocket-server/issues/26
class WebsocketServerThread(threading.Thread):

    def __init__(self, host, port):
        threading.Thread.__init__(self)
        self.server = SimpleWebSocketServer(host, port, NyankoRoverWebSocket)
        #self._isClosed = False
        self.setDaemon(True)

    def start(self):
        logging.info('WebsocketServerThread start')
        super(WebsocketServerThread, self).start()

    def run(self):
        logging.info('WebsocketServerThread run')
        self.server.serveforever()
        logging.info('WebsocketServerThread serveforever exited')

    def stop(self):
        logging.info('Stopping the WebSocket server...')
        self.server.close()

server = None
def start_websocket_server(port):
    global server
    logging.info('Starting the WebSocket server...')
    server = WebsocketServerThread('', port)
    server.start()
