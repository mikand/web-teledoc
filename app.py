#!/usr/bin/env python

from __future__ import unicode_literals

import time
import logging

from flask import Flask, render_template, Response, request
from flask_socketio import SocketIO, emit
from utils import requires_auth

from camera import Camera
from controller import LauncherController
from motors import MotorsController

app = Flask(__name__)
socketio = SocketIO(app)

cameras = {}

stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)
app.logger.addHandler(stream_handler)

cameras = {"0" : Camera(0), "1" : Camera(1)}
launcher = LauncherController()
motors = MotorsController()


@app.route('/')
@requires_auth
def index():
    """Video streaming home page."""
    return render_template('index.html')

@socketio.on('stream')
def stream(stream_id):
    if stream_id in cameras:
        data = {
            'id': stream_id,
            'raw': 'data:image/jpeg;base64,' + cameras[stream_id].get_frame_base64(),
            'timestamp': time.time()
        }
        emit('frame', data)
    else:
        print("ERROR: Invalid stream ID %s" % stream_id)


@app.route('/rocket', methods=["POST"])
@requires_auth
def rocket():
    """rocket route."""
    command_id = request.form["command_id"]
    if command_id == "up":
        launcher.step_up()
    elif command_id == "down":
        launcher.step_down()
    elif command_id == "left":
        launcher.step_left()
    elif command_id == "right":
        launcher.step_right()
    elif command_id == "fire":
        launcher.fire()
    else:
        raise KeyError("Unknown command provided")
    return "done"

@app.route('/car', methods=["POST"])
@requires_auth
def car():
    """car route."""
    direction = request.form["direction"]
    steering = request.form["steering"]

    if direction not in ["fwd", "bwd"]:
        return "error"
    if steering not in ["left", "right", "none"]:
        return "error"

    motors.do_step(direction, steering, duration=2.0)

    return "done"

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
