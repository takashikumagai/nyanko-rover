# Streams mjpeg video sourced from a V4L (Video for Linux) camera device

# Git cloned from the repo below and installed with 'python3 setup.py install'
# https://github.com/gebart/python-v4l2capture.git
import v4l2capture

import select
import io
from PIL import Image

class V4L2Camera:

    def __init__(self):
        self.video = v4l2capture.Video_device('/dev/video1')

        self.size_x, self.size_y = self.video.set_format(1280,1024)

        print('(v4l2) camera resolution: {} x {}'.format(self.size_x,self.size_y))

        num_buffers = 30
        self.video.create_buffers(num_buffers)

        print('(v4l2) {} buffers created'.format(num_buffers))

        self.video.queue_all_buffers()

        print('(v4l2) starting video capture')
    
    def start_capture(self):
        self.video.start()

    def stop_capture(self):
        self.video.close()

    def get_frame(self):

        # Wait until the video is ready for reading
        select.select((self.video,),(),())

        image_data = self.video.read_and_queue()

        #print('image data size: {}'.format(len(image_data)))
        #print('(v4l2) camera resolution: {} x {}'.format(self.size_x,self.size_y))

        image = Image.frombytes('RGB',(self.size_x,self.size_y),image_data)
        #print('image created from rgb bytes')
        frame = ''
        with io.BytesIO() as output:
            #print('saving image to memory')
            image.save(output, format='JPEG')
            frame = output.getvalue()
        #print('frame data size: {})'.format(len(contents)))
        return frame