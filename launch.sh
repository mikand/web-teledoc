#!/bin/sh

gunicorn --worker-class socketio.sgunicorn.GeventSocketIOWorker -b 0.0.0.0:5000 app:app
