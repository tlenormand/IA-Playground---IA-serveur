#!/usr/bin/env python3

import docker
import requests
import subprocess
import time
import os
import shutil

from classes.MasterClass import MasterClass
from formatters.formatter import formatter
from formatters.formatter_schemas import schema
from classes.Log import log


class Docker(MasterClass):
    def __init__(self, data):
        super().__init__(data)

        self.image = "tf"
        self.is_docker_running = self._get_docker_started()
        self.config = data.get('docker_config')
        self.ENV_VARIABLES = self._build_env_variables(data)

################################################################################
# Public methods
################################################################################

    def run_tf_container(self):
        try:
            if not self.is_docker_running:
                log.exception("DockerNotRunning", is_docker_running=self.is_docker_running)

            model_path_host = f"./{self.config.get('model_path', 'models/')}"
            model_path_container = f"/app/{self.config.get('model_path', 'models/')}"

            image_created = self._docker_create_image(self.image)
            if not image_created:
                log.exception("ImageCreationFailed", image=self.image)

            container_created = self._docker_create_container()
            if not container_created:
                log.exception("ContainerCreationFailed", image=self.image)

            env_created = self._docker_create_env()
            if not env_created:
                log.exception("EnvCreationFailed")

            folder_created = self._docker_create_folder(model_path_container)
            if not folder_created:
                log.exception("FolderCreationFailed", model_path_container=model_path_container)

            model_copied = self._copy_folder_host_to_docker(model_path_host, model_path_container)
            if not model_copied:
                log.exception("ModelCopyFailed", model_path_host=model_path_host, model_path_container=model_path_container)

            return super().get_docker_id()
        except Exception as e:
            log.exception(e)

    def run_tf_container_main(self):
        try:
            # TODO: Thread this
            process = subprocess.Popen(['docker', 'exec', super().get_docker_id(), 'python', 'main.py'],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                stdin=subprocess.DEVNULL,
                text=False,
            )

            return True
        except Exception as e:
            log.exception("RunTFContainerMainFailed")

    def stop_tf_container(self, docker_instance_ids):
        try:
            docker_id = self._find_running_container(docker_instance_ids)
            if not docker_id:
                log.exception("ContainerNotFound", docker_instance_ids=docker_instance_ids)

            model_path_host = f"./{self.config.get('model_path', 'models/')}"
            model_path_container = f"/app/{self.config.get('model_path', 'models/')}"

            env_file_updated = self._update_env_file("CAN_TRAIN", "False")
            if not env_file_updated:
                log.exception("EnvUpdateFailed")

            model_copied = self._copy_folder_docker_to_host(model_path_container, model_path_host)
            if not model_copied:
                log.exception("ModelCopyFailed", model_path_container=model_path_container, model_path_host=model_path_host)

            docker_stopped = self.stop_container()
            if not docker_stopped:
                log.exception("ContainerStopFailed", docker_id=docker_id)

            return True
        except Exception as e:
            log.exception(e)

    def send_model(self):
        try:
            endpoint = 'env/docker/get_model'
            data = {
                "user_id": super().get_user_id(),
                "model_name": super().get_model_name(),
                "docker_config": {
                    "id": super().get_docker_id()
                }
            }

            self._send(endpoint, data)

        except Exception as e:
            log.exception("SendModelFailed", endpoint=endpoint, data=data, exception=e)

################################################################################
# Private methods
################################################################################

    def _send(self, endpoint, data, options={}):
        try:
            if not formatter(endpoint, 'post', data):
                log.exception("validationFormatFailed", endpoint=endpoint, method='post', data=data)

            requests.post(self._get_url(endpoint), data=data)

        except Exception as e:
            if options.get('can_raise_exception', True):
                log.exception("SendFailed", endpoint=endpoint, data=data, exception=e)

            log.error("SendFailed", endpoint=endpoint, data=data, exception=e)

    def _get_docker_started(self):
        try:
            client = docker.from_env()
            client.containers.list()

            return True
        except Exception as e:
            return False

    def _send_id(self):
        endpoint = 'api/dockers/create'
        data = {
            "id": super().get_docker_id(),
            "userId": super().get_user_id(),
            "modelName": super().get_model_name()
        }

        self._send(endpoint, data, {'can_raise_exception': False})

    def _get_url(self, endpoint):
        if endpoint[:4] == 'api/':
            self.PORT = 3000
        elif endpoint[:4] == 'env/':
            self.PORT = 5000

        return f"{self.HOST}:{self.PORT}/{endpoint}"

    def _build_env_variables(self, data):
        atari_config = data.get('atari_config')
        docker_config = data.get('docker_config')
        env_variables = []

        if atari_config is None:
            return env_variables

        for key, value in atari_config.items():
            env_variables.extend(['-e', f'{key.upper()}={value}'])

        for key, value in docker_config.items():
            env_variables.extend(['-e', f'{key.upper()}={value}'])

        env_variables.extend(['-e', f'{"user_id".upper()}={super().get_user_id()}'])
        env_variables.extend(['-e', f'{"model_name".upper()}={super().get_model_name()}'])

        return env_variables

    def _file_string(self):
        file_string = "[DEFAULT]\n"

        for env_variable in self.ENV_VARIABLES:
            if env_variable != '-e':
                file_string += f"{env_variable}\n"

        return file_string

    def _update_env_file(self, key, value):
        docker_id = super().get_docker_id()
        if docker_id is None:
            return False

        command = f"sed -i 's/{key}=.*/{key}={value}/g' /app/.env"
        env_file_updated = subprocess.run(['docker', 'exec', docker_id, '/bin/sh', '-c', command])
        if env_file_updated.returncode != 0:
            return False

        return True

    def _docker_create_env(self):
        docker_id = super().get_docker_id()
        if docker_id is None:
            return False

        command = f"echo '{self._file_string()}' > /app/.env"
        env_file_created = subprocess.run(['docker', 'exec', docker_id, '/bin/sh', '-c', command])
        if env_file_created.returncode != 0:
            return False

        return True

    def _docker_create_folder(self, path):
        docker_id = super().get_docker_id()
        if docker_id is None:
            return False

        folder_exists = subprocess.run(['docker', 'exec', docker_id, 'test', '-d', path], capture_output=True, text=True)
        if folder_exists.returncode != 0:
            folder_created = subprocess.run(['docker', 'exec', docker_id, 'mkdir', path], capture_output=True, text=True)
            if folder_created.returncode != 0:
                return False

        return True

    def _copy_folder_host_to_docker(self, path_from, path_to):
        docker_id = super().get_docker_id()
        if docker_id is None:
            return False

        folder_name = super().get_model_full_name()
        if not folder_name:
            return False

        folder_exists = subprocess.run(['docker', 'exec', docker_id, 'test', '-d', path_to], capture_output=True, text=True)
        if folder_exists.returncode != 0:
            return False

        folder_copied = subprocess.run(['docker', 'cp', f'{path_from}{folder_name}', f"{docker_id}:{path_to}"], capture_output=True, text=True)
        if folder_copied.returncode != 0:
            return False

        return True
    
    def _copy_folder_docker_to_host(self, path_from, path_to):
        docker_id = super().get_docker_id()
        if docker_id is None:
            return False
        
        folder_name = super().get_model_full_name()
        if not folder_name:
            return False

        if not os.path.exists(path_to):
            os.makedirs(path_to)

        folder_copied = subprocess.run(['docker', 'cp', f"{docker_id}:{path_from}{folder_name}", f"{path_to}{folder_name}_tmp"], capture_output=True, text=True)
        if folder_copied.returncode != 0:
            if os.path.exists(f"{path_to}{folder_name}_tmp"):
                shutil.rmtree(f"{path_to}{folder_name}_tmp")
            return False

        shutil.rmtree(f"{path_to}{folder_name}")
        shutil.move(f"{path_to}{folder_name}_tmp", f"{path_to}{folder_name}")

        return True

    def _docker_create_image(self, image=None):
        if image is None:
            image = self.image

        image_exists = subprocess.run(['docker', 'image', 'inspect', self.image], capture_output=True, text=True)
        if image_exists.returncode != 0:
            image_created = subprocess.run(['docker', 'build', '-t', 'tf', '-f', 'Docker/dockerfile.tf', '.'], check=True)
            if image_created.returncode != 0:
                return False

        return True

    def _docker_create_container(self, image=None):
        if image is None:
            image = self.image

        container_created = subprocess.run(['docker', 'run', '--rm', '-idt', *self.ENV_VARIABLES, self.image], stdout=subprocess.PIPE, check=False, capture_output=False)
        if container_created.returncode != 0:
            return False

        updated = subprocess.run(['docker', 'exec', container_created.stdout.strip().decode('utf-8'), 'pip', 'install', '--upgrade', 'pip'], capture_output=True, text=True, check=True)
        if updated.returncode != 0:
            return False

        container_requirements = subprocess.run(['docker', 'exec', container_created.stdout.strip().decode('utf-8'), 'pip', 'install', '--ignore-installed', '-r', 'Docker/docker.tf.requirements.python.txt'], capture_output=True, text=True, check=True)
        if container_requirements.returncode != 0:
            return False

        docker_id = container_created.stdout.strip().decode('utf-8')
        if docker_id is None:
            return False

        log.write(f"Container {docker_id} created")
        super().set_docker_id(docker_id)
        self._send_id()

        return True

    def stop_container(self):
        docker_id = super().get_docker_id()
        if docker_id is None:
            return False

        docker_stopped = subprocess.run(['docker', 'stop', docker_id], capture_output=True, text=True, check=True)
        if docker_stopped.returncode != 0:
            return False

        return True

    def _find_running_container(self, docker_instance_ids):
        try:
            client = docker.from_env()
            running_containers = client.containers.list()
            running_container_ids = [container.id for container in running_containers]

            for container_id in docker_instance_ids:
                if container_id in running_container_ids:
                    super().set_docker_id(container_id)

                    return container_id

            return False
        except Exception as e:
            log.exception(e)
