#!/usr/bin/env python

from __future__ import unicode_literals

import time
import logging

from flask import Flask, render_template, Response, request
from flask_socketio import SocketIO, emit, disconnect
from utils import requires_auth, socket_requires_auth

from camera import Camera
from controller import LauncherController
from motors import MotorsController

app = Flask(__name__)
socketio = SocketIO(app)

stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)
app.logger.addHandler(stream_handler)

cameras = {"0" : Camera(0), "1" : Camera(1)}
launcher = LauncherController()
motors = MotorsController()
rtts = {}

RTTS_INCREMENT = 1.15

def get_client_id():
    return 0

@app.route('/')
@requires_auth
def index():
    """Video streaming home page."""
    return render_template('index.html')

@socketio.on('connected')
def connected():
    rtts[get_client_id()] = 1

@socketio.on('disconnect')
def unconnect():
    try:
        del rtts[get_client_id()]
    except KeyError:
        pass


@socketio.on('rttpong')
@socket_requires_auth
def pong(data):
    rtts[get_client_id()] = min((time.time() - data["timestamp"]), 1)
    emit('rttpong', 'done')

@socketio.on('stream')
@socket_requires_auth
def stream(stream_id):
    stream_id = str(stream_id)
    if stream_id in cameras:
        data = {
            'id': stream_id,
            'raw': 'data:image/jpeg;base64,' + cameras[stream_id].get_frame_base64(),
        }
        emit('frame', data)
    else:
        print("ERROR: Invalid stream ID %s" % stream_id)


@socketio.on('motor')
@socket_requires_auth
def motor(command):
    emit('rttping', {"timestamp": time.time()})
    direction = command["direction"]
    steering = command["steering"]

    if direction not in ["fwd", "bwd", "none"]:
        print('ERROR in motor: wrog direction')
    elif steering not in ["left", "right", "none"]:
        print('ERROR in motor: wrong steering')
    else:
        duration = 1
        if get_client_id() in rtts:
            duration = rtts[get_client_id()] * RTTS_INCREMENT
        motors.do_step(direction, steering, duration=duration)


@socketio.on('rocket')
@socket_requires_auth
def rocket(data):
    """rocket socket"""
    emit('rttping', {"timestamp": time.time()})
    command = data["command"]

    if command not in ["stop", "up", "down", "right", "left", "fire"]:
        print('ERROR in rocket: invalid command')
    else:
        if command == "fire":
            launcher.fire()
        else:
            duration = 0.05
            if get_client_id() in rtts:
                duration = rtts[get_client_id()] * RTTS_INCREMENT
            launcher.step(command, duration)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
