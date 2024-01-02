#!/usr/bin/env python3

from flask import Blueprint, jsonify

from controllers.controller import controller


test_bp = Blueprint('test', __name__)

@test_bp.route('/env/test', methods=['GET'])
def get_test():
    return jsonify(controller('env/test', 'GET', ''))
