#!/usr/bin/env python3

import logging

from flask import Flask, request

from classes._Logs import _log
from routes.atari_route import atari_bp
from routes.test_route import test_bp
from routes.model_route import model_bp
from routes.docker_route import docker_bp
from validators.validator import validator

app = Flask(__name__)
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)


# Middleware
@app.before_request
def before_request():
    _log.log_request(request)
    validator(request)

# Middleware
@app.after_request
def after_request(response):
    _log.log_response(response)
    return response

# Register blueprints
app.register_blueprint(atari_bp)
app.register_blueprint(test_bp)
app.register_blueprint(model_bp)
app.register_blueprint(docker_bp)

if __name__ == '__main__':
    app.run(debug=True)
