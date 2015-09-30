#!/usr/bin/env python
from flask import Flask, render_template, Response
from flask import request

from utils import requires_auth

from camera import Camera
from controller import LauncherController

app = Flask(__name__)

@app.route('/')
@requires_auth
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
@requires_auth
def video_feed():
    """Video streaming route."""
    return Response(gen(Camera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/command', methods=["POST"])
@requires_auth
def command():
    """command route."""
    command_id = request.form["command_id"]
    c = LauncherController()
    if command_id == "up":
        c.step_up()
    elif command_id == "down":
        c.step_down()
    elif command_id == "left":
        c.step_left()
    elif command_id == "right":
        c.step_right()
    elif command_id == "fire":
        c.fire()
    else:
        raise KeyError("Unknown command provided")
    return "done"


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=False, threaded=True)
