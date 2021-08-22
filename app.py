#!/usr/bin/env python
from importlib import import_module
import os
from flask import Flask, render_template, Response, make_response
import argparse

# import camera driver
if os.environ.get('CAMERA'):
    Camera = import_module('camera_' + os.environ['CAMERA']).Camera
else:
    from camera_opencv import Camera


# Raspberry Pi camera module (requires picamera package)
# from camera_pi import Camera

# run the process on the backend

def arguments():
    ap = argparse.ArgumentParser()

    ap.add_argument("-s", "--save", type=int,
                    default=1,
                    help="have 0 to not save videos and 1 to save them.")
    ap.add_argument("--sms", type=int,
                    default=1,
                    help="have 0 not to send emails and texts when objects are detected, 1 for them to be sent.")

    return vars(ap.parse_args())


app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
    """Video streaming home page."""
    return render_template('index.html')


def gen(camera):
    """Video streaming generator function."""
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


def text_gen(camera):
    """sending ok while keeping process alive."""
    while True:
        _ = camera.get_frame()
        yield "ok"


@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(Camera(arguments())),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/stay_alive')
def stay_alive():
    """sending minimal payload and keeping the process alive"""
    return Response(text_gen(Camera(arguments())),
                    mimetype='text/xml')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8111, threaded=True)
