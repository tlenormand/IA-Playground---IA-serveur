#!/usr/bin/env python3

from flask import Blueprint, jsonify, request

from controllers.controller import controller


atari_bp = Blueprint('atari', __name__)

@atari_bp.route('/env/atari/train/start', methods=['POST'])
def post_atari_train():
    return jsonify(controller('env/atari/train/start', 'POST', request.json))

@atari_bp.route('/env/atari/train/stop', methods=['POST'])
def post_atari_stop():
    return jsonify(controller('env/atari/train/stop', 'POST', request.json))

@atari_bp.route('/env/atari/create', methods=['POST'])
def post_atari_create():
    return jsonify(controller('env/atari/create', 'POST', request.json))

@atari_bp.route('/env/atari/reset', methods=['POST'])
def post_atari_reset():
    return jsonify(controller('env/atari/reset', 'POST', request.json))

@atari_bp.route('/env/atari/step', methods=['POST'])
def post_atari_step():
    return jsonify(controller('env/atari/step', 'POST', request.json))
