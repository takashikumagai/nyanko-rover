# Streams mjpeg video sourced from a V4L (Video for Linux) camera device

# Installed this by executing the command below
# - pipenv install -e git+https://github.com/gebart/python-v4l2capture.git#egg=v4l2capture
# Note: before using pipenv, this was installed with these steps
# - git clone https://github.com/gebart/python-v4l2capture.git
# - python3 setup.py install
import v4l2capture

import select
import io
import time
from PIL import Image

class V4L2Camera:

    def __init__(self,device_path):
        device_path_to_use = device_path if device_path is not None else '/dev/video0'

        self.video = v4l2capture.Video_device(device_path_to_use)

        x = 1280
        y = 1024
        self.size_x, self.size_y = self.video.set_format(x, y, fourcc='MJPG')

        print('(v4l2) camera resolution: {} x {}'.format(self.size_x,self.size_y))

        num_buffers = 30
        self.video.create_buffers(num_buffers)

        print('(v4l2) {} buffers created'.format(num_buffers))

        self.video.queue_all_buffers()

        print('(v4l2) all buffers queued')

    def start_capture(self):
        print('(v4l2) starting video capture')
        self.video.start()

    def stop_capture(self):
        self.video.stop()

    def close(self):
        self.video.close()

    def get_frame(self):

        # Wait until the video is ready for reading
        select.select((self.video,),(),())

        image_data = ''
        try:
            image_data = self.video.read_and_queue()
        except Exception:
            print('video.read_and_queue() threw. Returning an empty frame data in 1s.')
            time.sleep(1)

        #print('image data size: {}'.format(len(image_data)))
        #print('(v4l2) camera resolution: {} x {}'.format(self.size_x,self.size_y))

        return image_data

        #image = Image.frombytes('RGB',(self.size_x,self.size_y),image_data)
        #print('image created from rgb bytes')
        #frame = ''
        #with io.BytesIO() as output:
        #    print('saving image to memory')
        #    image.save(output, format='JPEG')
        #    frame = output.getvalue()
        #print('frame data size: {})'.format(len(contents)))
        #return frame
