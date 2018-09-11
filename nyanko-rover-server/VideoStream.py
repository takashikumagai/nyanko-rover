#!/usr/bin/env python3

import logging
import platform
import RPiCamera
import TestImageCamera
import V4L2Camera


class VideoStream:

    def __init__(self,camera_device,video_resolution='640x480'):

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


        logging.info('Setting up streaming output')
        #self.streaming_output = StreamingOutput()

        logging.info('starting the recording')
        #self.camera.start_recording(self.streaming_output, format='mjpeg')

        #self.stop_streaming = False

    def stop_recording(self):
        self.camera.stop_capture()
        pass
        #if self.camera != None:
        #    self.camera.stop_recording()

    def start_streaming(self,http_request_handler):

        self.camera.start_capture()

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
          while True:#self.stop_streaming == False:
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
