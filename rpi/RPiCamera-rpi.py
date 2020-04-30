import logging
import sys
import threading
import io
import picamera

def is_camera_available():
  camera = None
  try:
    camera = picamera.PiCamera()
  except picamera.exc.PiCameraMMALError:
    logging.info('picamera mmal error')
    return False
  except picamera.exc.PiCameraError:
    logging.info('picamera error')
    return False
  except:
    logging.info('An unknown picamera error')
    return False
  finally:
    if camera is not None:
      logging.info('Closing the camera')
      camera.close()
      return True
    else:
      return False

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
                # set the entire contents of the buffer (bytes) to frame
                self.frame = self.buffer.getvalue()
                self.condition.notify_all()
            self.buffer.seek(0)
        return self.buffer.write(buf)

class RPiCamera:

  def __init__(self, params):
    self.pi_camera = None

    # Check if the params dictionary has all the required keys
    if params and 'resolution' in params and 'framerate' in params and 'quality' in params:
      pass
    else:
      logging.error("The 'params' does not have all the required keys. PiCamera will not be initialized.")

    self.params = params

    try:
      logging.info(f'Creating pi camera: {self.params}')
      self.pi_camera = picamera.PiCamera(
        resolution = self.params['resolution'],
        framerate = self.params['framerate']
      )
    except:
      logging.error('failed to init pi camera. Error:', sys.exc_info()[0])
      return

    logging.info('Setting up streaming output')
    self.streaming_output = StreamingOutput()

  def start_capture(self):

    if self.pi_camera is None:
      logging.info('start_capture !pi_camera')
      return

    if self.pi_camera.recording:
      logging.info('Already started recording. Nothing to do')
      return

    logging.info('starting the recording')
    #self.pi_camera.resolution = (320, 240)
    self.pi_camera.start_recording(self.streaming_output, format='mjpeg', quality=self.params['quality'])
    logging.info('started recording')
    timeout = 5
    self.pi_camera.wait_recording(timeout)

    self.stop_streaming = False

  def stop_capture(self):
    if self.pi_camera.recording:
      self.pi_camera.stop_recording()
    else:
      print('Not recording. Nothing to do.')

  def close(self):
    print('(TestImageCamera) closing the device')
    if self.pi_camera is None:
      logging.info('pi_camera is None. Nothing to close')
      return
    self.pi_camera.close()

  def get_frame(self):

    if self.pi_camera is None or self.pi_camera.closed:
      return b''

    with self.streaming_output.condition:
      self.streaming_output.condition.wait()
      return self.streaming_output.frame

  def get_resolution(self):
    if self.pi_camera is None or self.pi_camera.closed:
        return (0,0)

    # self.pi_camera.resolution is a PiResolution (namedtuple derivative)
    # but is converted to a tuple
    return self.pi_camera.resolution

  def get_framerate(self):
    if self.pi_camera is None or self.pi_camera.closed:
        return 0

    # self.pi_camera.framerate is a PiCameraFraction class object
    # which looks like this: PiCameraFraction(24, 1)
    return self.pi_camera.framerate[0]

  def get_quality(self):
    if self.pi_camera is None or self.pi_camera.closed:
        return 0

    return self.params['quality']
