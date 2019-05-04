import logging
from camera import RPiCamera
from camera import TestImageCamera
from camera import V4L2Camera

def create_camera(camera_device):
    logging.info('Creating a camera object:' + camera_device)
    if camera_device == 'picamera':
        return RPiCamera.RPiCamera()
    elif camera_device == 'stub':
        return TestImageCamera.TestImageCamera(['img1.jpg','img2.jpg','img3.jpg'])
    elif camera_device == 'dualfisheye-stub':
        return TestImageCamera.TestImageCamera(['dualfisheye1.jpg','dualfisheye2.jpg','dualfisheye3.jpg'])
    else:
        return V4L2Camera.V4L2Camera(camera_device)
