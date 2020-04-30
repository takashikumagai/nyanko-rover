import os
from camera import RPiCamera

def is_camera_available(camera_device):
    if camera_device == 'picamera':
        return RPiCamera.is_camera_available()
    else:
        return os.path.exists(camera_device)
