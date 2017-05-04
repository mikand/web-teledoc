#!/bin/sh

#gunicorn --worker-class gevent -w 1 -b 0.0.0.0:5000 app:app
sudo python app.py
