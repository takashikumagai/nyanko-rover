import logging
import threading
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

class RPiCamera:

  def __init__(self):
    try:
      video_resolution = '640x480'
      self.pi_camera = picamera.PiCamera(resolution=video_resolution, framerate=24)
    except:
      logging.error('faled to init pi camera.')
      return

    logging.info('Setting up streaming output')
    self.streaming_output = StreamingOutput()

    logging.info('starting the recording')
    self.pi_camera.start_recording(self.streaming_output, format='mjpeg')

    self.stop_streaming = False

  def get_frame(self):
    with self.streaming_output.condition:
      self.streaming_output.condition.wait()
      return self.streaming_output.frame
