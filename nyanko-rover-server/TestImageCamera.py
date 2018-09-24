import time

class TestImageCamera:

  def read_file(self,pathname):
    with open(pathname,'rb') as f:
      return f.read()

  def __init__(self,filename_list):
    #self.frames = [self.read_file('sample_images/'+f+'.jpg') for f in ['img1','img2','img3']]
    self.frames = [self.read_file('sample_images/'+f) for f in filename_list]

  def start_capture(self):
    print('(TestImageCamera) starting video capture - nothing to do')
    pass

  def stop_capture(self):
    print('(TestImageCamera) stopping video capture - nothing to do')
    pass

  def close(self):
    print('(TestImageCamera) closing the device - nothing to do')
    pass

  def get_frame(self):
    time.sleep(0.05)
    return self.frames[ int(time.clock()) % 3 ]

if __name__ == '__main__':
  print('TestImageCamera')
  # Syntax/sanity check
  cam = TestImageCamera()
  print(len(cam.get_frame()))
