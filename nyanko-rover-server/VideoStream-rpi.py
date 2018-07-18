#!/usr/bin/env python3

import threading
import logging
import io
import picamera


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


class VideoStream:

    def __init__(self,video_resolution='640x480'):

        logging.info('Initializing camera')
        self.camera = picamera.PiCamera(resolution=video_resolution, framerate=24)

        #Uncomment the next line to change your Pi's Camera rotation (in degrees)
        #mycamera.rotation = 90


        logging.info('Setting up streaming output')
        self.streaming_output = StreamingOutput()

        logging.info('starting the recording')
        self.camera.start_recording(self.streaming_output, format='mjpeg')

        self.stop_streaming = False

    def stop_recording(self):
        self.camera.stop_recording()

    def start_streaming(self,http_request_handler):
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
            with self.streaming_output.condition:
              self.streaming_output.condition.wait()
              frame = self.streaming_output.frame
            http_request_handler.wfile.write(b'--FRAME\r\n')
            http_request_handler.send_header('Content-Type', 'image/jpeg')
            http_request_handler.send_header('Content-Length', len(frame))
            http_request_handler.end_headers()
            http_request_handler.wfile.write(frame)
            http_request_handler.wfile.write(b'\r\n')
        except Exception as e:
          logging.warning('Removed streaming client %s: %s', "???", str(e))#self.client_address, str(e))
