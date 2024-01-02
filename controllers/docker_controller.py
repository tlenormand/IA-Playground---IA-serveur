#!/usr/bin/env python3

import docker

from classes.Docker import Docker


def create_docker_post_controller(data):
    Docker_instance = Docker(data)
    Docker_instance.run_tf_container()

    return {'success': False, 'message': 'Not implemented'}

def get_model_docker_running_post_controller(data):
    try:
        client = docker.from_env()
        running_containers = client.containers.list()
        running_container_ids = [container.id for container in running_containers]

        result = []
        for container_id in data.get('docker_instance_ids'):
            if container_id in running_container_ids:
                result.append(container_id)

        return {'success': True, 'data': result}

    except Exception as e:
        return {'success': False, 'message': str(e)}
