#!/usr/bin/env python3

from flask import Blueprint, jsonify, request

from controllers.controller import controller


docker_bp = Blueprint('docker', __name__)

@docker_bp.route('/env/dockers/create', methods=['POST'])
def post_docker_create():
    return jsonify(controller('env/dockers/create', 'POST', request.json))

@docker_bp.route('/env/dockers/get_model', methods=['POST'])
def post_docker_get_model():
    return jsonify(controller('env/dockers/get_model', 'POST', request.json))

@docker_bp.route('/env/dockers/running', methods=['POST'])
def post_docker_running():
    return jsonify(controller('env/dockers/running', 'POST', request.json))
