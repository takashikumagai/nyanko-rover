#!/usr/bin/env python3

import http.server
import os
import logging
import inspect

from SimpleWebSocketServer import SimpleWebSocketServer, WebSocket

import motor_control


def guess_script_file_directory():
  filename = inspect.getframeinfo(inspect.currentframe()).filename
  path = os.path.dirname(os.path.abspath(filename))
  logging.info('guess: {}'.format(path))
  return path

#Create custom HTTPRequestHandler class
class NyankoRoverHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):

  def send_response_and_header(self,content_type):
      #send code 200 response
      self.send_response(200)

      #send header first
      self.send_header('Content-type',content_type)
      self.end_headers()

  #handle GET command
  def do_GET(self):
    rootdir = guess_script_file_directory()
    try:
      logging.debug('self.path {}'.format(self.path))
      # if self.path == '/' or self.path.endswith('.html'):
      #   mypath = 'index.html' if self.path == '/' else self.path
      #   with open(os.path.join(rootdir,mypath)) as f:
      #     s = f.read()
      #
      #     send_response_and_header('text/html')
      #
      #     #send file content to client
      #     logging.debug('file content: {}'.format(s))
      #     self.wfile.write(s.encode('utf-8'))
      #     #self.wfile.write(b"<html><body><h1>nyanko server</h1></body></html>")
      #     return
      #
      # elif self.path.endswith('.js'):
      #   with open(os.path.join(rootdir,mypath)) as f:
      #     s = f.read()
      #     send_response_and_header('application/javascript')
      #     logging.debug('js content: {}'.format(s))
      #     self.wfile.write(s.encode('utf-8'))
      #     return

      if self.path.startswith('/forward'):
        print('forward action requested')
        motor_control.start_motor_forward(10)
      elif self.path.startswith('/stop'):
        print('stopping the motor')
        motor_control.stop_motor()
      elif self.path.startswith('/reset'):
        print('Resetting')
        motor_control.stop_motor()
      else:
        super(NyankoRoverHTTPRequestHandler,self).do_GET()


    except IOError:
      motor_control.stop_motor()
      self.send_error(404, 'file not found')

class SimpleEcho(WebSocket):

    def handleMessage(self):
        print("Message received: {}".format(self.data))
        # echo message back to client
        self.sendMessage(self.data)

    def handleConnected(self):
        print(self.address, 'connected')

    def handleClose(self):
        print(self.address, 'closed')

def start():

  logging.basicConfig(filename='nyankoroverserver.log', level=logging.DEBUG)

  motor_control.init()

  logging.info('Setting up the server...')
  port = 13412
  print('port: {}'.format(port))
  #server_address = ('127.0.0.1', port)
  server_address = ('', port)
  httpd = http.server.HTTPServer(server_address, NyankoRoverHTTPRequestHandler)

  logging.info('Starting the server...')
  httpd.serve_forever()

def run():

  try:
    start()
  finally:
    logging.info('Cleaning up...')
    motor_control.cleanup()

if __name__ == '__main__':
  run()

