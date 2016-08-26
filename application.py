#!/usr/bin/env python2.7
# coding=utf-8
from __future__ import unicode_literals
from flask import Flask, jsonify, redirect, send_from_directory, request
from sys import exit, stderr
from os import getenv

try:
    import config
except ImportError:
    stderr.write("Please copy config.example.py to config.py and edit the file.")
    exit(1)

from shared import db
from controllers import *
from utils import Error

if config.google_api_key == '':
    stderr.write("GCM disabled, please enter the google api key for gcm")

app = Flask(__name__)
app.debug = config.debug or getenv('FLASK_DEBUG', 0) is 1
app.config['SQLALCHEMY_DATABASE_URI'] = config.database_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)


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
    return jsonify(Error.RATE_TOOFAST)


app.register_blueprint(subscription)
app.register_blueprint(message)
app.register_blueprint(service)
if config.google_api_key is not "":
    app.register_blueprint(gcm)

if __name__ == '__main__':
    app.run()
