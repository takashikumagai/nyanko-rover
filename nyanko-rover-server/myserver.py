#!/usr/bin/env python3

import http.server
import http.cookies
import socketserver
import sys
import os
import logging
import inspect
import threading
import time
import random
import json

# Third-party Python libraries
from SimpleWebSocketServer import SimpleWebSocketServer, WebSocket
import vcgencmd

# Proprietary Python modules
import cmdutil
import motor_control
import NetworkStatusReporter
import VideoStream
import networktool


httpd = None
ws_server = None
motor_controller_thread = None
web_server_thread = None
websocket_server_thread = None
video_stream = None

# Stores entries like this: { 'sid': '123456' }
# i.e. each element is a dictionary
sesison_info_list = []

def file_exists(pathname):
  if not os.path.exists(pathname):
    print('Path "{}" does not exist.'.format(pathname))
    logging.debug('Path "{}" does not exist.'.format(pathname))
    return False
  elif not os.path.isfile(pathname):
    print('Path "{}" is not a file.'.format(pathname))
    logging.debug('Path "{}" is not a file.'.format(pathname))
    return False
  else:
    return True

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
def register_session_info(headers):
  global sesison_info_list
  sid = str(random.randint(0,999999999999)).zfill(12)
  sesison_info_list.append({'user-agent':headers.get('User-Agent'), 'sid':sid})
  print('session_info_list updated: ' + str(sesison_info_list))
  logging.info('session_info_list updated: ' + str(sesison_info_list))
  return sid

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
          if(self.is_password_valid(self.headers)):

              # Authentication succeeded
              print('Issuing a session ID')
              logging.info('Issuing a session ID')
              # Hands out a session ID to the client
              sid = register_session_info(self.headers)

              # Add a customer header representing
              #self.send_header('Nyanko-Rover-Session-ID',sid)

              #self.send_empty_response_and_header()

              # f = open('blank.html', 'rb')
              # fs = os.fstat(f.fileno())
              # self.send_response_and_header('text/html',fs[6])
              # self.copyfile(f, self.wfile)
              # f.close()

              xml_text = '<?xml version="1.0" encoding="UTF-8"?>\n<sid>' + sid + '</sid>'
              encoded = xml_text.encode('utf-8')
              self.send_response_and_header('text/xml',len(encoded))
              self.wfile.write(encoded)
              self.wfile.flush()
              logging.debug(str(self))
              return

          else:
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
        # Always call self.wfile.write AFTER self.end_headers() otherwise responseText JS receives
        # will have everything including Content-type and others as a single string.
        self.wfile.write(encoded)
        #html = b'<html><head>myhtml</head><body>myhtmlbody</body></html>'
        #self.wfile.write(html)
        #print('length: {}'.format(len(encoded)))
        #self.send_response_and_header('text/html',len(html))
        self.send_response_and_header('text/xml',len(encoded))
        #return xmltext

      elif self.path.startswith('/hw-status'):
        print('Querying server hardware status.')
        hw_status = {
          "uptime": 0,
          "temp": vcgencmd.measure_temp(),
          "cpu_usage": 0,
          "camera": {"supported": vcgencmd.get_camera('supported'), "detected": vcgencmd.get_camera('detected')},
          "ip": '0.0.0.0',
          "public_ip": '0.0.0.0'
        }

        #hw_status = '<?xml version="1.0" encoding="UTF-8"?>\n<info>' + 'nyanko' + '</info>'
        text = json.dumps(hw_status)
        encoded = text.encode('utf-8')
        self.send_response_and_header('application/json',len(encoded))
        self.wfile.write(encoded)
        self.wfile.flush()
        return

      elif self.path == '/stream.mjpg':
        video_stream.start_streaming(self)

      else:
        print('Delegating request to super class (path: {})'.format(self.path))
        logging.info('Delegating request to super class (path: {})'.format(self.path))
        super(NyankoRoverHTTPRequestHandler,self).do_GET()


    except IOError:
      motor_control.stop_motor()
      self.send_error(404, 'file not found')

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
      session_info = [item for item in sesison_info_list if user_agent_value == item['user-agent']]
      if 0 < len(session_info) and session_info[0]['sid'] == client_sid:
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

  def is_password_valid(self,headers):
    result = [item for item in headers.items() if item[0] == 'my-password']
    print(headers.items())
    logging.debug(str(headers.items()))
    print('search result:', result)
    logging.debug('search result: ' + str(result))
    if len(result) == 1:
      if result[0][1] == 'abc':
        return True
      else:
        logging.debug('pw: ' + result[0][1])
        print('pw: ' + result[0][1])
        return False
    else:
      logging.debug('len(result)' + str(len(result)))
      print('len(result)' + str(len(result)))
      return False
  
  def return_index_html_page(self):
    f = open('index.html', 'rb')
    fs = os.fstat(f.fileno())
    self.send_response_and_header('text/html',fs[6])
    self.copyfile(f, self.wfile)
    f.close()

  def return_login_page(self):
    print('Returning login page.')
    logging.debug('Returning login page.')
    if not file_exists('auth.html'):
      return
    with open('auth.html', 'rb') as f:
      fs = os.fstat(f.fileno())
      self.send_response_and_header('text/html',fs[6])
      self.copyfile(f, self.wfile)


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
  global motor_controller_thread
  global web_server_thread
  global websocket_server_thread

  log_format = '%(asctime)-15s %(thread)d %(message)s'
  logging.basicConfig(filename='nyankoroverserver.log', level=logging.DEBUG, format=log_format)

  video_stream = VideoStream.VideoStream()

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
    video_stream.stop_recording()
    #motor_control.cleanup()

if __name__ == '__main__':
  run()
