#!/usr/bin/env python2.7
# coding=utf-8
from __future__ import unicode_literals
from flask import Flask, jsonify, redirect, send_from_directory, request
from sys import exit, stderr
from os import getenv

try:
    import config
except ImportError:
    stderr.write("FATAL: Please copy config.example.py to config.py and edit the file.")
    exit(1)

from shared import db
from controllers import *
from utils import Error

gcm_enabled = True
if config.google_api_key == '':
    stderr.write("WARNING: GCM disabled, please enter the google api key for gcm")
    gcm_enabled = False
if not isinstance(config.google_gcm_sender_id, int):
    stderr.write("WARNING: GCM disabled, sender id is not an integer")
    gcm_enabled = False
elif config.google_gcm_sender_id == 0:
    stderr.write('WARNING: GCM disabled, invalid sender id found')
    gcm_enabled = False


app = Flask(__name__)
app.debug = config.debug or int(getenv('FLASK_DEBUG', 0)) > 0
app.config['SQLALCHEMY_DATABASE_URI'] = config.database_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
with app.app_context():
    db.engine.execute("SET NAMES 'utf8mb4' COLLATE 'utf8mb4_unicode_ci'")


@app.route('/')
def index():
    return redirect('http://docs.pushjet.io')


@app.route('/robots.txt')
@app.route('/favicon.ico')
def robots_txt():
    return send_from_directory(app.static_folder, request.path[1:])


@app.route('/version')
def version():
    with open('.git/refs/heads/master', 'r') as f:
        return f.read(7)


@app.errorhandler(429)
def limit_rate(e):
    return Error.RATE_TOOFAST


app.register_blueprint(subscription)
app.register_blueprint(message)
app.register_blueprint(service)
if gcm_enabled:
    app.register_blueprint(gcm)

if __name__ == '__main__':
    app.run()
