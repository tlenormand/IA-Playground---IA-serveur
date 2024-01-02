#!/usr/bin/env python3

import subprocess

from classes._Logs import _log
from classes.Model import Model


def create_model_post_controller(data):
    Model_instance = Model(data)
    Model_instance.build_model()
    model_full_name = Model_instance.save_model()

    data = { 'model_name': model_full_name }

    return {'success': True, 'message': 'Model created', 'data': data}

def delete_model_post_controller(data):
    model_full_name = f"{data.get('user_id')}__{data.get('model_name')}"
    model_path = f"./models/{model_full_name}"

    try:
        subprocess.run(["rm", "-rf", model_path], capture_output=True, text=True, check=True)
    except Exception as e:
        _log.write(f"Error when delete model: {e}")
        return {'success': False, 'message': f"Error when delete model", 'data': {'modelName': model_full_name}}
    
    return {'success': True, 'message': 'Model deleted', 'data': {'modelName': model_full_name}}

def get_model_docker_post_controller(data):
    docker_config = data.get('docker_config')
    docker_id = docker_config.get('id')
    model_full_name = f"{data.get('user_id')}__{data.get('model_name')}"
    model_path_host = f"./models/{model_full_name}"
    model_path_container = f"models/"
    try:
        subprocess.run(["docker", "cp", f"{docker_id}:app/{model_path_container}", model_path_host], capture_output=True, text=True, check=True)
    except Exception as e:
        _log.write(f"Error when get model: {e}")
        return {'success': False, 'message': f"Error when get model", 'data': {'modelName': model_full_name}}

    return {'success': True, 'message': 'Model got', 'data': {'modelName': model_full_name}}
