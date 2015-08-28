#!/usr/bin/env python

from flask import Flask, render_template, Response

from camera import Camera
from controller import LauncherController

app = Flask(__name__)


@app.route('/')
def index():
    """Video streaming home page."""
    return render_template('index.html')


def gen(camera):
    """Video streaming generator function."""
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/video_feed')
def video_feed():
    """Video streaming route."""
    return Response(gen(Camera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/command_up')
def command_up():
    """Up command route."""
    c = LauncherController()
    c.step_up()
    return "done"

@app.route('/command_down')
def command_down():
    """Up command route."""
    c = LauncherController()
    c.step_down()
    return "done"

@app.route('/command_left')
def command_left():
    """Left command route."""
    c = LauncherController()
    c.step_left()
    return "done"

@app.route('/command_right')
def command_right():
    """Up command route."""
    c = LauncherController()
    c.step_right()
    return "done"

@app.route('/command_fire')
def command_fire():
    """Up command route."""
    c = LauncherController()
    c.fire()
    return "done"


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
