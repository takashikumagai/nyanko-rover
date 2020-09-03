from flask import render_template, Response, request, flash, redirect, url_for
from flask_login import current_user, login_user, logout_user, login_required
from app import app
from app.models import User
from app.login import LoginForm
import logging
import json
import os

import psutil
import vcgencmd

# Proprietary Python modules
import cmdutil
import motor_control
import Headlamp
from camera import CameraFactory
# from event_driven_camera import CameraFactory
from camera import CameraAvailabilityChecker
import HWStatusReporter
from app.login import LoginForm

camera = None
headlamp = Headlamp.Headlamp()

@app.route('/')
@app.route('/index')
@login_required
def index():
    return render_template('index.html')

@app.route('/forward')
@login_required
def forward():
    logging.debug('driving forward')
    motor_control.start_motor_forward(10)
    return "forward"
    # motor_control.start_motor_forward(10)

@app.route('/backward')
@login_required
def backward():
    logging.debug('driving backward')
    motor_control.start_motor_backward(10)
    return "backward"
    # motor_control.start_motor_backward(10)

@app.route('/stop')
@login_required
def stop():
    logging.debug('stopping the motor')
    motor_control.stop_motor()
    motor_control.set_steering(0)
    return "stop"
    # motor_control.stop_motor()
    # motor_control.set_steering(0)

@app.route('/steer')
@login_required
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
@login_required
def shutdown():
    logging.debug('shutdown')
    return "shutdown"

@app.route('/reboot')
@login_required
def reboot():
    logging.debug('reboot')
    return "reboot"

@app.route('/hw-status')
@login_required
def hw_status():
    logging.debug('hw-status')
    hw_status_reporter = HWStatusReporter()
    return hw_status_reporter.get_hw_status()

@app.route('/take-photo')
@login_required
def take_photo():
    logging.debug('take-photo')
    cmdutil.exec_cmd_async(['raspistill', '-o', 'myphoto.jpg'], on_photo_saved)

def get_default_camera_params():
    return {
        'resolution': (320,240),
        'framerate': 24,
        'quality': 0
    }

def load_camera_params():
    if os.path.exists('video-stream-options.json'):
        with open('video-stream-options.json') as f:
            return json.load(f)
    else:
        return get_default_camera_params()

def create_camera(params):

    if len(params) == 0:
        params = load_camera_params()

    with open('server_params.json','r') as f:
        server_params = json.load(f)
        # Decide if we can go with the specified one or need to fall back to the stub
        specified = server_params['front_camera']
        camera_to_create = specified if CameraAvailabilityChecker.is_camera_available(specified) else 'stub'
        camera = CameraFactory.create_camera(camera_to_create, params)
        return camera

    return None

def write_camera_params_to_file(camera):
    with open('video-stream-options.json', 'w') as f:
        params = {
            'resolution': camera.get_resolution(),
            'framerate': camera.get_framerate(),
            'quality': camera.get_quality()
        }
        logging.info(f'Saving camera params to file: {params}')
        json.dump(params, f)

def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/stream.mjpg')
@login_required
def stream_mjpg():
    global camera
    if camera is None:
        camera = create_camera({})
        camera.start_capture()
    logging.info('streaming')
    return Response(gen(camera),
            mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/get-video-stream-options')
@login_required
def video_stream_options():
    global camera
    params = {}
    if camera is None:
        params = load_camera_params()
    else:
        params = {
            'resolution': camera.get_resolution(),
            'framerate': camera.get_framerate(),
            'quality': camera.get_quality()
        }
    return params

@app.route('/start-video-stream', methods=['POST'])
@login_required
def start_video_stream():
    global camera
    if camera is None:
        params = request.get_json()
        params['resolution'] = tuple(params['resolution'])
        logging.info(f'start-video-stream {params}')
        camera = create_camera(params)

    camera.start_capture()

    write_camera_params_to_file(camera)

    return {}

@app.route('/stop-video-stream', methods=['POST'])
@login_required
def stop_video_stream():
    global camera
    if camera is None:
        logging.info('stop_video_stream: no camera')
        return {}
    else:
        camera.stop_capture()
    return {}

@app.route('/reset-video-stream', methods=['POST'])
@login_required
def reset_video_stream():
    global camera
    params = request.get_json()
    params['resolution'] = tuple(params['resolution'])
    logging.info(f'reset-video-stream {params}')
    if camera is None:
        logging.info('reset_video_stream: no camera')
    else:
        camera.stop_capture()
        camera.close()

    camera = create_camera(params)
    camera.start_capture()

    write_camera_params_to_file(camera)

    return {}

@app.route('/close-video-stream', methods=['POST'])
@login_required
def close_video_stream():
    global camera
    if camera is None:
        logging.info('No stream to close')
        return {}
    camera.stop_capture()
    camera.close()
    return {}

@app.route('/get-available-camera-types')
@login_required
def get_available_camera_types():
    with open('server_params.json','r') as f:
        server_params = json.load(f)
        available_camera_types = {}

        # Check if a front-facing camera is available
        front_camera_available = 'front_camera' in server_params and CameraAvailabilityChecker.is_camera_available(server_params['front_camera'])
        available_camera_types['front'] = 'yes' if front_camera_available else 'no'

        # Check if a spherical camera is available
        spherical_camera_available = 'spherical_camera' in server_params and CameraAvailabilityChecker.is_camera_available(server_params['spherical_camera'])
        available_camera_types['spherical'] = 'yes' if spherical_camera_available else 'no'

        logging.info(f'available camera types: {available_camera_types}')
        return available_camera_types

    return {}

@app.route('/headlamp', methods=['GET', 'POST'])
@login_required
def headlight():
    #global headlamp
    if request.method == 'GET':
        # Return the current brightness
        logging.info(f'Current headlight brightness: {headlamp.brightness}')
        return {'brightness': headlamp.brightness}
    elif request.method == 'POST':
        # Set the brightness
        params = request.get_json()
        logging.info(f'/headlamp POST {params}')
        if 'brightness' in params:
            logging.info(f"Changing headlight brightness: {params['brightness']}")
            headlamp.set_brightness(params['brightness'])
        else:
            logging.warning('/headlamp: brightness not specified')
        return {'brightness': headlamp.brightness}
    else:
        return {}

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and form.password.data == 'admin-user-password':
            flash('You are logged in.', 'success')
            login_user(user, remember=form.remember.data)

            # If the user has been redirected to login page after attempting to access
            # another page, redirect the user to that page.
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Login unsuccessful.', 'danger')

    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))