#!/usr/bin/env python3

import http.server
import socketserver
import os
import logging
import inspect
import threading
import time
import io
import picamera

from SimpleWebSocketServer import SimpleWebSocketServer, WebSocket

# Proprietary Python modules
import cmdutil
import motor_control
import NetworkStatusReporter
import networktool


httpd = None
ws_server = None
motor_controller_thread = None
mycamera = None
output = None

def guess_script_file_directory():
  filename = inspect.getframeinfo(inspect.currentframe()).filename
  path = os.path.dirname(os.path.abspath(filename))
  logging.info('guess: {}'.format(path))
  return path

def on_photo_saved(stdout,stderr):
  logging.info('Photo saved to file.')

def take_photo():
  logging.info('Taking a photo...')
  cmdutil.exec_cmd_async(['raspistill', '-o', 'myphoto.jpg'], on_photo_saved)

class StreamingOutput(object):
    def __init__(self):
        self.frame = None
        self.buffer = io.BytesIO()
        self.condition = threading.Condition()

    def write(self, buf):
        if buf.startswith(b'\xff\xd8'):
            # New frame, copy the existing buffer's content and notify all
            # clients it's available
            self.buffer.truncate()
            with self.condition:
                self.frame = self.buffer.getvalue()
                self.condition.notify_all()
            self.buffer.seek(0)
        return self.buffer.write(buf)

#Create custom HTTPRequestHandler class
class NyankoRoverHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):

  # def __init__(self):
  #     print('NyankoRoverHTTPRequestHandler init')

  def send_response_and_header(self,content_type,contnet_length):
      #send code 200 response
      self.send_response(200)

      #send header first
      self.send_header('Content-type',content_type)
      self.send_header("Content-Length", str(contnet_length))
      self.send_header("Last-Modified", self.date_time_string(1522536578))
      self.end_headers()

  #handle GET command
  def do_GET(self):

    global video_stream

    rootdir = guess_script_file_directory()
    try:
      #print('self.path {}, thread {}'.format(self.path, threading.current_thread().ident))

      if 'mjpg' in self.path:
        print('mjpg in path')
        logging.debug('mjpg in self.path')

      if self.path.startswith('/forward'):
        logging.debug('driving forward')
        motor_control.start_motor_forward(10)
      elif self.path.startswith('/stop'):
        logging.debug('stopping the motor')
        motor_control.stop_motor()
        motor_control.set_steering(0)
      elif self.path.startswith('/backward'):
        logging.debug('driving backward')
        motor_control.start_motor_backward(10)
      elif self.path.startswith('/steer'):
        logging.debug('steering {}'.format(str(self.path)))
        if 0 <= self.path.find('dir=left'):
          motor_control.set_steering(90)
        elif 0 <= self.path.find('dir=right'):
          motor_control.set_steering(-90)
      elif self.path.startswith('/reset'):
        print('Resetting')
        #motor_control.stop_motor()
      elif self.path.startswith('/take_photo'):
        print('Taking a photo')
        take_photo()
      elif self.path.startswith('/server_address'):
        print('server_address requested')
        with open('myaddress.xml','w') as xmlfile:
          xmlfile.write('<?xml version="1.0" encoding="UTF-8"?>\n')
          xmlfile.write('<nyanko>' + networktool.get_ip() + '</nyanko>')
        f = open('myaddress.xml', 'rb')
        self.send_response(200)
        self.send_header("Content-type", 'text/xml')
        fs = os.fstat(f.fileno())
        self.send_header("Content-Length", str(fs[6]))
        self.send_header("Last-Modified", self.date_time_string(fs.st_mtime))
        self.end_headers()
        self.copyfile(f, self.wfile)
        f.close()
        return

        xmltext = '<?xml version="1.0" encoding="UTF-8"?><p>nyanko</p>'
        encoded = xmltext.encode('utf-8')
        self.wfile.write(encoded)
        #html = b'<html><head>myhtml</head><body>myhtmlbody</body></html>'
        #self.wfile.write(html)
        #print('length: {}'.format(len(encoded)))
        #self.send_response_and_header('text/html',len(html))
        self.send_response_and_header('text/xml',len(encoded))
        #return xmltext

      elif self.path == '/stream.mjpg':
        logging.info('Streaming (mjpg).')
        print('Streaming video.')
        self.send_response(200)
        self.send_header('Age', 0)
        self.send_header('Cache-Control', 'no-cache, private')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
        self.end_headers()
        try:
          while True:
            with output.condition:
              output.condition.wait()
              frame = output.frame
            self.wfile.write(b'--FRAME\r\n')
            self.send_header('Content-Type', 'image/jpeg')
            self.send_header('Content-Length', len(frame))
            self.end_headers()
            self.wfile.write(frame)
            self.wfile.write(b'\r\n')
        except Exception as e:
          logging.warning('Removed streaming client %s: %s', self.client_address, str(e))

      else:
        super(NyankoRoverHTTPRequestHandler,self).do_GET()


    except IOError:
      motor_control.stop_motor()
      self.send_error(404, 'file not found')


class NyankoRoverWebSocket(WebSocket):

    #def __init__(self):
    #    super(NyankoRoverWebSocket,self).__init__()
    #     WebSocket.__init__(self)
        #self.network_status_reporter = None

    def handleMessage(self):
        print("ws:message received: {}".format(self.data))

        # Unpack the data
        motor = self.data[0:1] # 'f' fwd/back or 's' for steering
        value = int(float(self.data[1:]))
        print('motor: {}, speed/steer: {}'.format(motor,value))
        if motor == 'f':
          motor_control.set_fwd_back_motor_speed(value)
        elif motor == 's':
          motor_control.set_steering(value)

    def handleConnected(self):
        print(self.address, 'ws:connected')

        self.network_status_reporter = NetworkStatusReporter.NetworkStatusReporter(self)
        self.network_status_reporter.start()

    def handleClose(self):
        print(self.address, 'ws:closed')

        if self.network_status_reporter != None:
            self.network_status_reporter.stop()
        


class StreamingServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True


# Starts a web server and a WebSocket server on their own threads.
# In other words, invocation of this function will create two new threads.
def start():

  log_format = '%(asctime)-15s %(thread)d %(message)s'
  logging.basicConfig(filename='nyankoroverserver.log', level=logging.DEBUG, format=log_format)

  print('Initializing camera')
  global mycamera
  #with picamera.PiCamera(resolution='640x480', framerate=24) as mycamera:
  mycamera = picamera.PiCamera(resolution='640x480', framerate=24)
    
  print('Setting up streaming output')
  global output
  output = StreamingOutput()
  #Uncomment the next line to change your Pi's Camera rotation (in degrees)
  #mycamera.rotation = 90
  print('starting the recording')
  mycamera.start_recording(output, format='mjpeg')
  # try:
  #   address = ('', 8000)
  #   server = StreamingServer(address, StreamingHandler)
  #   server.serve_forever()
  # finally:
  #   mycamera.stop_recording()

  # Set up and start the motor controller
  logging.info('Setting up the motor controller...')
  motor_control.init()
  motor_controller_thread = threading.Thread(target = motor_control.run)
  motor_controller_thread.start()

  # Set up and start the web server
  logging.info('Setting up the web server...')
  http_port = 13412
  print('web server port: {}'.format(http_port))
  #server_address = ('127.0.0.1', port)
  server_address = ('', http_port)
  #httpd = http.server.HTTPServer(server_address, NyankoRoverHTTPRequestHandler)
  httpd = StreamingServer(server_address, NyankoRoverHTTPRequestHandler)
  web_server_thread = threading.Thread(target = httpd.serve_forever)


  logging.info('Starting the server...')
  web_server_thread.start()

  # Set up and start the WebSocket server
  logging.info('Setting up the WebSocket server...')
  ws_port = 9792
  ws_server = SimpleWebSocketServer('', ws_port, NyankoRoverWebSocket)
  print("Starting a WebSocket server (port: {}).".format(ws_port))
  websocket_server_thread = threading.Thread(target = ws_server.serveforever)
  websocket_server_thread.start()

def run():

  global mycamera

  try:
    start()
    while(True):
      time.sleep(1)
  except KeyboardInterrupt:
    print("Keyboard interrupt")
    httpd.shutdown()

    # WebSocket shutdown
    ws_server.close()

    # Shut down the motor controller and wait for the thread to terminate
    motor_control.shutdown()
    motor_controller_thread.join()

    logging.info('Stopping the camera recording...')
    mycamera.stop_recording()

  finally:
    print('in "finally" block')
    logging.info('Cleaning up...')
    #motor_control.cleanup()

if __name__ == '__main__':
  run()
