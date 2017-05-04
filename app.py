#!/usr/bin/env python

from __future__ import unicode_literals

import time
import logging

from flask import Flask, render_template, Response, request
from flask_socketio import SocketIO, emit
from utils import requires_auth

from camera import Camera
from controller import LauncherController

app = Flask(__name__)
socketio = SocketIO(app)

cameras = {}

stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)
app.logger.addHandler(stream_handler)

camera = Camera()
launcher = LauncherController()


@app.route('/')
@requires_auth
def index():
    """Video streaming home page."""
    return render_template('index.html')

@socketio.on('stream')
def stream(foo):
    data = {
        'id': 0,
        'raw': 'data:image/jpeg;base64,' + camera.get_frame_base64(),
        'timestamp': time.time()
    }

    emit('frame', data)

@app.route('/command', methods=["POST"])
@requires_auth
def command():
    """command route."""
    command_id = request.form["command_id"]
    c = launcher
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
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
