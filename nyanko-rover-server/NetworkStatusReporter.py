#!/usr/bin/env python3

import time
import threading
import json
import networktool
from SimpleWebSocketServer import SimpleWebSocketServer, WebSocket


class MyClass:
    pass


class NetworkStatusReporter:

    def __init__(self,_websocket):
        self.terminateThread = False
        self.websocket = _websocket
        self.thread = None
        self.statusCheckIntervalInSeconds = 5

    # \return a dictionary containing the wifi connection information.
    def get_wifi_connection_info(self):
        ssid = networktool.get_connected_network_ssid()
        signal = networktool.get_connected_network_signal_strength()
        info = {'ssid': ssid, 'signal_strength': signal }
        #print('connection info: {}'.format(info))
        return json.dumps(info)

    def send_wifi_connection_info(self,info):
        msg = '#' + info

        try:
            #print('Sending: ' + str(msg))
            self.websocket.sendMessage(msg)
        except Exception:
            print('An exception occurred (tried to send data to client via websocket)')
        finally:
            pass
            #print('Network info: ' + str(msg))
    
    def start(self):
        self.thread = threading.Thread(target=self.thread_main_loop, args=())
        self.thread.start()

    def thread_main_loop(self):

        prev_info = None

        while(self.terminateThread == False):

            info = self.get_wifi_connection_info()

            if prev_info != info:
                #print('Change detected')
                self.send_wifi_connection_info(info)
                prev_info = info

            time.sleep(self.statusCheckIntervalInSeconds)

    def stop(self):
        self.terminateThread = True
        self.thread.join(timeout=5.0)

class WebSocketStub:

    def sendMessage(self,msg):
        print('sending msg via websocket(stub): {}'.format(msg))

def run_test():
    wss = WebSocketStub()
    reporter = NetworkStatusReporter(wss)

    reporter.start()
    time.sleep(20)
    reporter.stop()


if __name__ == '__main__':
    run_test()
