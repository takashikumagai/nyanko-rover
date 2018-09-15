#!/usr/bin/env python3

import logging
import platform
import RPiCamera
import TestImageCamera
import V4L2Camera
import time


class VideoStream:

    def __init__(self,camera_device,video_resolution='640x480'):

        self.camera = None
        self.is_capture_on = False

        try:
            logging.info('Initializing camera')
            if camera_device == 'picamera':
                self.camera = RPiCamera.RPiCamera()
            elif camera_device == 'stub':
                self.camera = TestImageCamera.TestImageCamera()
            else:
                self.camera = V4L2Camera.V4L2Camera(camera_device)
        except Exception as e:
            logging.info('Camera init failed - device: {}, exception: {}'.format(camera_device,e))
            return

        #Uncomment the next line to change your Pi's Camera rotation (in degrees)
        #mycamera.rotation = 90

        logging.info('starting the recording')
        #self.camera.start_recording(self.streaming_output, format='mjpeg')

    # Gives the camera device chance to do any init/settings before starting the thread loop
    # the client calls start_streaming() after this to initiate the streaming thread.
    def start_capture(self):

        if self.camera is None:
            return

        self.is_capture_on = True
        self.camera.start_capture()

    def stop_capture(self):

        self.is_capture_on = False

        time.sleep(0.5)

        self.camera.stop_capture()
        #if self.camera != None:
        #    self.camera.stop_recording()
    
    def close(self):
        self.camera.stop_capture()
        self.camera.close()

    # Enters the stream main loop and keeps returning frame data indefinitely
    # until stop_capture() is called.
    def start_streaming(self,http_request_handler):

        self.start_capture()

        if self.camera == None:
            logging.info('camera not available')
            return

        logging.info('Streaming (mjpg).')
        print('Streaming video.')
        http_request_handler.send_response(200)
        http_request_handler.send_header('Age', 0)
        http_request_handler.send_header('Cache-Control', 'no-cache, private')
        http_request_handler.send_header('Pragma', 'no-cache')
        http_request_handler.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
        http_request_handler.end_headers()
        try:
          while self.is_capture_on:
            #with self.streaming_output.condition:
            #  self.streaming_output.condition.wait()
            #  frame = self.camera.get_frame()
            frame = self.camera.get_frame()
            http_request_handler.wfile.write(b'--FRAME\r\n')
            http_request_handler.send_header('Content-Type', 'image/jpeg')
            http_request_handler.send_header('Content-Length', len(frame))
            http_request_handler.end_headers()
            http_request_handler.wfile.write(frame)
            http_request_handler.wfile.write(b'\r\n')
        except Exception as e:
          logging.warning('Removed streaming client %s: %s', "???", str(e))#self.client_address, str(e))

        print('leaving streaming thread function.')