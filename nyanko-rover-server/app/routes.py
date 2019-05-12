from flask import render_template, Response, request
from app import app
import logging
import json

import psutil
import vcgencmd

# Proprietary Python modules
import cmdutil
import motor_control
from camera import CameraFactory

camera = None

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/forward')
def forward():
    logging.debug('driving forward')
    motor_control.start_motor_forward(10)
    return "forward"
    # motor_control.start_motor_forward(10)

@app.route('/backward')
def backward():
    logging.debug('driving backward')
    motor_control.start_motor_backward(10)
    return "backward"
    # motor_control.start_motor_backward(10)

@app.route('/stop')
def stop():
    logging.debug('stopping the motor')
    motor_control.stop_motor()
    motor_control.set_steering(0)
    return "stop"
    # motor_control.stop_motor()
    # motor_control.set_steering(0)

@app.route('/steer')
def steer():
    logging.debug('steering')
    params = request.args.to_dict()
    dir = params.get('dir')
    if dir == 'left':
        motor_control.set_steering(95)
    elif dir == 'right':
        motor_control.set_steering(-95)
    else:
        logging.debug("!dir")
    return "steering"

@app.route('/shutdown')
def shutdown():
    logging.debug('shutdown')
    return "shutdown"

@app.route('/reboot')
def reboot():
    logging.debug('reboot')
    return "reboot"

@app.route('/hw-status')
def hw_status():
    logging.debug('hw-status')
    hw_status = {
        "uptime": get_uptime(),
        "temp": vcgencmd.measure_temp(),
        "cpu_usage": psutil.cpu_percent(),
        "camera": {"supported": vcgencmd.get_camera('supported'), "detected": vcgencmd.get_camera('detected')},
        "ip": '0.1.2.3',
        "public_ip": '4.5.6.7'
    }
    return "hw-status"

@app.route('/take-photo')
def take_photo():
    logging.debug('take-photo')
    cmdutil.exec_cmd_async(['raspistill', '-o', 'myphoto.jpg'], on_photo_saved)

def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/stream.mjpg')
def stream_mjpg():
    global camera
    if camera is None:
        with open('server_params.json','r') as f:
            server_params = json.load(f)
            camera = CameraFactory.create_camera(server_params['front_camera'])
            camera.start_capture()
    logging.info('streaming')
    return Response(gen(camera),
            mimetype='multipart/x-mixed-replace; boundary=frame')