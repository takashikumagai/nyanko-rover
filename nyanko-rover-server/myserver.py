#!/usr/bin/env python3

import http.server
import os
import logging
import inspect

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

