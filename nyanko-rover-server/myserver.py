#!/usr/bin/env python3

import http.server
import http.cookies
import socketserver
import sys
import os
import subprocess
import logging
import inspect
import threading
import time
import random
import json

# Third-party Python libraries
from SimpleWebSocketServer import SimpleWebSocketServer, WebSocket
import psutil
import vcgencmd

# Proprietary Python modules
import cmdutil
import motor_control
import NetworkStatusReporter
import VideoStream
import networktool
import filesystem_utils


httpd = None
ws_server = None
motor_controller_thread = None
web_server_thread = None
websocket_server_thread = None
video_stream = None

# Miscellaneous parameters
server_params = {}

# Stores entries like this: { 'sid': '123456' }
# i.e. each element is a dictionary
sesison_info_list = []

guest_pin = ''

def guess_script_file_directory():
  filename = inspect.getframeinfo(inspect.currentframe()).filename
  path = os.path.dirname(os.path.abspath(filename))
  #logging.info('guess: {}'.format(path))
  return path

def on_photo_saved(stdout,stderr):
  logging.info('Photo saved to file.')

def take_photo():
  logging.info('Taking a photo...')
  cmdutil.exec_cmd_async(['raspistill', '-o', 'myphoto.jpg'], on_photo_saved)

# Returns a 6-digit PIN
def generate_random_pin():
  return str(random.randint(0,999999)).zfill(6)

# Returns a new session ID
def register_session_info(headers,user_type):
  global sesison_info_list
  sid = str(random.randint(0,999999999999)).zfill(12)
  print('New sid: {}'.format(sid))
  logging.debug('New sid: {}'.format(sid))
  sesison_info_list.append({'sid':sid, 'user-type':user_type, 'user-agent':headers.get('User-Agent')})
  print('session_info_list updated: ' + str(sesison_info_list))
  logging.info('session_info_list updated: ' + str(sesison_info_list))
  return sid

# Returns a string representing the system uptime
def get_uptime():
  raw = subprocess.check_output('uptime').decode('utf8').replace(',','')
  words = raw.split()
  if 3 <= len(words):
    return words[2]
  else:
    return '?'

#Create custom HTTPRequestHandler class
class NyankoRoverHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):

  # def __init__(self):
  #     print('NyankoRoverHTTPRequestHandler init')

  def send_empty_response_and_header(self):
      self.send_response(204)
      #self.send_header('Content-type','text/plain')
      self.end_headers()

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
    global video_stream_360

    rootdir = guess_script_file_directory()
    try:
      print('self.path {}, thread {}'.format(self.path, threading.current_thread().ident))
      print('🍪 cookie: {}'.format(self.headers.get('Cookie')))

      #logging.info('#HEADERS (as string): ',self.headers.as_string())
      #logging.info('#HEADERS (items): ',self.headers.items())

      # Check if the path has either
      # 1. has a valid sesison info, or
      # 2. a static resource or a script which is not an html file.
      # - 2 allows .js/.jpg/ files to be returned without session info (no way to request these with session info)
      #   whereas index.html and other API calls (motor controls, etc) require session info
      if self.validate_session_info(self.headers):
          print('✓ valid sid')
          logging.debug('✓ valid sid')
          pass
      elif self.path.startswith('/auth'):
          print('🔑 Authenticating.')
          logging.debug('🔑 Authenticating.')

          # The user has sent a password

          registered = self.register_client(self.headers)

          if not registered:
            logging.debug('authentication failed. Returning an empty string instead of a session ID')
            self.send_response_and_header('text/plain',0)
          return

      else:
          print('login is required')
          logging.debug('login is required')
          self.return_login_page()
          return

      # if self.path.startswith('/main'):
      #   print('returning index.html (home)')
      #   logging.debug('returning index.html (home)')
      #   self.return_index_html_page()
      #   return

      if 'mjpg' in self.path:
        print('📹 mjpg in path')
        logging.debug('📹 mjpg in self.path')

      if self.path.startswith('/auth'):
        client_sid = get_sid_from_cookie(self.headers)
        print('Authentication request from a client which already has an sid: {}'.format(client_sid))
        logging.debug('Authentication request from a client which already has an sid: {}'.format(client_sid))

        xml_text = '<?xml version="1.0" encoding="UTF-8"?>\n<r>already-authenticated</r>'
        encoded = xml_text.encode('utf-8')
        self.send_response_and_header('text/xml',len(encoded))
        self.wfile.write(encoded)
        self.wfile.flush()
        logging.debug('response xml: {}'.format(str(self)))
        return
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
      elif self.path.startswith('/pin'):

        #if not self.is_admin(self.headers):
        #  return

        pin = {"pin":self.get_guest_password()}
        text = json.dumps(pin)
        print('Returning pin info: {}'.format(str(text)))
        logging.debug('Returning pin info: {}'.format(str(text)))
        encoded = text.encode('utf-8')
        self.send_response_and_header('application/json',len(encoded))
        self.wfile.write(encoded)
        self.wfile.flush()
        return

      elif self.path.startswith('/shutdown'):
        print('shutdown request received')
        #subprocess.check_output('sudo shutdown now')
        pass
      elif self.path.startswith('/reboot'):
        print('reboot request received')
        pass
      elif self.path.startswith('/hw-status'):
        print('Querying server hardware status.')
        hw_status = {
          "uptime": get_uptime(),
          "temp": vcgencmd.measure_temp(),
          "cpu_usage": psutil.cpu_percent(),
          "camera": {"supported": vcgencmd.get_camera('supported'), "detected": vcgencmd.get_camera('detected')},
          "ip": '0.1.2.3',
          "public_ip": '4.5.6.7'
        }

        text = json.dumps(hw_status)
        #text = '<?xml version="1.0" encoding="UTF-8"?>\n<abc>123</abc>'
        print('hw_status: ' + text)
        encoded = text.encode('utf-8')
        self.send_response_and_header('application/json',len(encoded))
        self.wfile.write(encoded)
        self.wfile.flush()
        return

      elif self.path == '/stream.mjpg':
        video_stream.start_streaming(self)

      elif self.path == '/stream360.mjpg':
        video_stream_360.start_streaming(self)

      elif self.path.startswith('/stream?'):
        op = self.path[len('/stream?'):]
        self.control_stream(video_stream,op)
        encoded = json.dumps({"nyanko":0}).encode('utf-8')
        self.send_response_and_header('application/json',len(encoded))
        self.wfile.write(encoded)
        self.wfile.flush()
        return

      elif self.path.startswith('/stream360?'):
        op = self.path[len('/stream360?'):]
        self.control_stream(video_stream_360,op)
        encoded = json.dumps({"nyanko":0}).encode('utf-8')
        self.send_response_and_header('application/json',len(encoded))
        self.wfile.write(encoded)
        self.wfile.flush()
        return
  
      else:
        print('Delegating request to super class (path: {})'.format(self.path))
        logging.info('Delegating request to super class (path: {})'.format(self.path))
        super(NyankoRoverHTTPRequestHandler,self).do_GET()


    except IOError:
      motor_control.stop_motor()
      self.send_error(404, 'file not found')

  def get_sid_from_cookie(self,headers):
    cookie = headers.get('Cookie')
    if cookie == None:
      return None

    print('myCookie: {}'.format(str(cookie)))
    sc = http.cookies.SimpleCookie()
    sc.load(str(cookie))
    if 'nrsid' in sc:
      return sr['nrsid'].value
    else:
      print('sid not found in cookie')
      return None

  def validate_session_info(self,headers):
    global sesison_info_list

    if len(sesison_info_list) == 0:
      print("No session info on the server")
      logging.info("No session info on the server")
      return False

    cookie = headers.get('Cookie')
    print('vsi() Cookie: {}'.format(str(cookie)))
    sc = http.cookies.SimpleCookie()
    sc.load(str(cookie))
    if 'nrsid' in sc:
      # The cookie has 'nrsid'
      client_sid = sc['nrsid'].value
      user_agent = [item for item in headers.items() if item[0] == 'User-Agent']
      user_agent_value = user_agent[0][1]
      session_info = [item for item in sesison_info_list if client_sid == item['sid']]
      if 0 < len(session_info) and session_info[0]['user-agent'] == user_agent_value:
        print("session info validated: ", str(session_info[0]))
        logging.info("session info validated: " + str(session_info[0]))
        return True
      else:
        print("invalid session id")
        logging.info("invalid session id")
        return False
    else:
      print("nrsid not found in cookie")
      print(str(cookie))
      logging.info("nrsid not found in header")
      return False

  def get_password_from_header(self,headers):
    result = [item for item in headers.items() if item[0] == 'my-password']
    print('searched pw from header. Result: {}'.format(str(result)))
    logging.debug('searched pw from header. Result: {}'.format(str(result)))
    print('pw: {}'.format(result[0][1]))
    logging.debug('pw: {}'.format(result[0][1]))
    if len(result) == 1:
      return result[0][1]
    else:
      return None

  def return_index_html_page(self):
    f = open('index.html', 'rb')
    fs = os.fstat(f.fileno())
    self.send_response_and_header('text/html',fs[6])
    self.copyfile(f, self.wfile)
    f.close()

  def return_login_page(self):
    print('Returning login page.')
    logging.debug('Returning login page.')
    if not filesystem_utils.file_exists('auth.html'):
      return
    with open('auth.html', 'rb') as f:
      fs = os.fstat(f.fileno())
      self.send_response_and_header('text/html',fs[6])
      self.copyfile(f, self.wfile)

  def is_valid_admin_password(self,pw):
    if pw == 'abc':
      return True
    else:
      return False

  def get_guest_password(self):
    global guest_pin
    if len(guest_pin) == 0:
      guest_pin = generate_random_pin()
    return guest_pin

  def is_valid_guest_password(self,pw):
    if pw == get_guest_password():

      # A user was authenticated with the PIN
      # Change the PIN so that guests need to login with a different PIN
      guest_pin = generate_random_pin()

      return True
    else:
      return False

  def register_client(self,headers):
    print('register_client: {}'.format(str(headers.items())))
    logging.debug('register_client: {}'.format(str(headers.items())))

    received_password = self.get_password_from_header(headers) # The password client sent to the server
    if received_password is None:
      return False

    sid = ''
    if self.is_valid_admin_password(received_password):
      # Register the user as the admin
      sid = register_session_info(headers,'admin')
    elif self.is_valid_guest_password(received_password):
      sid = register_session_info(headers,'guest')
    else:
      print('Invalid password: {}'.format(received_password))
      logging.debug('Invalid password: {}'.format(received_password))
      return False

    if 0 < len(sid):
      # Authentication succeeded
      print('Returning a session ID')
      logging.info('Returning a session ID')
      # Hands out a session ID to the client
      xml_text = '<?xml version="1.0" encoding="UTF-8"?>\n<sid>{}</sid>'.format(sid)
      encoded = xml_text.encode('utf-8')
      self.send_response_and_header('text/xml',len(encoded))
      self.wfile.write(encoded)
      self.wfile.flush()
      logging.debug(str(self))
      return True

  def control_stream(self,video_stream,op):

    if op == 'close':
      video_stream.close()
    else:
      print('Unsupported operation: {}'.format(op))
    ##elif op == 'start':
    ##  video_stream.start_streaming()
    ##elif op == 'stop':
    ##  video_stream.stop_recording()

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

  global httpd
  global ws_server
  global video_stream
  global video_stream_360
  global motor_controller_thread
  global web_server_thread
  global websocket_server_thread
  global server_params

  log_format = '%(asctime)-15s %(thread)d %(message)s'
  logging.basicConfig(filename='nyankoroverserver.log', level=logging.DEBUG, format=log_format)

  with open('server_params.json','r') as f:
    server_params = json.load(f)

  video_stream = VideoStream.VideoStream(server_params['front_camera'])
  video_stream_360 = VideoStream.VideoStream('/dev/v4l/by-id/usb-Arashi_Vision_Insta360_Air-video-index0')

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

  global httpd
  global ws_server
  global video_stream
  global video_stream_360
  global motor_controller_thread
  global web_server_thread
  global websocket_server_thread

  try:
    start()
    while(True):
      time.sleep(1)
    logging.info("the end of try block")
  except KeyboardInterrupt:
    logging.info("Keyboard interrupt exception")

  except:
    logging.info('Exception on the nyanko-rover-server: ',sys.exc_info())

  else:
    logging.info('There was no exception.')

  finally:
    print('in "finally" block')
    logging.info('Cleaning up...123123123')

    logging.info('Shutting down the web server.')
    try:
      httpd.shutdown()
      web_server_thread.join()
    except KeyboardInterrupt:
      pass

    # WebSocket shutdown
    logging.info('Closing the web socket server.')
    try:
      ws_server.close()
      websocket_server_thread.join()
    except KeyboardInterrupt:
      pass

    # Shut down the motor controller and wait for the thread to terminate
    logging.info('Terminating the motor controller thread.')
    motor_control.shutdown()
    try:
      motor_controller_thread.join()
    except KeyboardInterrupt:
      pass

    logging.info('Stopping the camera recording...')
    video_stream.stop_capture()
    #motor_control.cleanup()

if __name__ == '__main__':
  run()
