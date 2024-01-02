#!/usr/bin/env python3

from flask import Blueprint, jsonify, request

from controllers.controller import controller


model_bp = Blueprint('model', __name__)

@model_bp.route('/env/model/create', methods=['POST'])
def post_model_create():
    return jsonify(controller('env/model/create', 'POST', request.json))

@model_bp.route('/env/model/delete', methods=['POST'])
def post_model_delete():
    return jsonify(controller('env/model/delete', 'POST', request.json))
