#!/usr/bin/env python3

import docker
import requests
import subprocess
import time
import os
import shutil

from classes._Logs import _log
from classes.MasterClass import MasterClass
from formatters.formatter import formatter
from formatters.formatter_schemas import schema


class Docker(MasterClass):
    def __init__(self, data):
        super().__init__(data)

        self.is_docker_running = self.get_docker_started()
        self.config = data.get('docker_config')
        self.ENV_VARIABLES = self.build_env_variables(data)

    def get_docker_started(self):
        try:
            client = docker.from_env()
            client.containers.list()
            return True

        except Exception as e:
            _log.write(f"Erreur lors de la vérification de l'état de Docker : {e}")
            return False

    def send_id(self):
        try:
            endpoint = 'api/dockers/create'
            data = {
                "id": super().get_docker_id(),
                "userId": super().get_user_id(),
                "modelName": super().get_model_name()
            }

            if formatter(endpoint, 'post', data):
                requests.post(self.get_url(endpoint), data=data)
            else:
                _log.write(f"Erreur de validation du format de la requête {endpoint}")

        except Exception as e:
            _log.write(f"Erreur lors de l'envoi de l'ID du conteneur : {e}")
    
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

            if formatter(endpoint, 'post', data):
                requests.post(self.get_url(endpoint), data=data)
            else:
                _log.write(f"Erreur de validation du format de la requête {endpoint}")

        except Exception as e:
            _log.write(f"Erreur lors de l'envoi du modèle : {e}")

    def get_url(self, endpoint):
        if endpoint[:4] == 'api/':
            self.PORT = 3000
        elif endpoint[:4] == 'env/':
            self.PORT = 5000

        return f"{self.HOST}:{self.PORT}/{endpoint}"

    def build_env_variables(self, data):
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

    def run_tf_container(self):
        try:
            # check image exists
            check_image = subprocess.run(['docker', 'image', 'inspect', 'tf'], capture_output=True, text=True)

            # Build image if not exists
            if check_image.returncode != 0:
                subprocess.run(['docker', 'build', '-t', 'tf', '-f', 'Docker/Dockerfile.tf', '.'], check=True)

            env_variables = self.ENV_VARIABLES

            model_path_host = f"./{self.config.get('model_path', 'models/')}{super().get_model_full_name()}"
            model_path_container = f"{self.config.get('model_path', 'models/')}"

            result = subprocess.run(
                ['docker', 'run', '--rm', '-idt', *env_variables, 'tf'],
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                stdin=subprocess.DEVNULL,
                text=True,
                check=False,
                capture_output=False
            )

            if result.returncode != 0:
                return False

            docker_id = result.stdout.strip()
            super().set_docker_id(docker_id)
            self.send_id()

            # copy two times the model to the container otherwise the model is not found...
            subprocess.run(["docker", "cp", model_path_host, f"{docker_id}:app/{model_path_container}"], capture_output=False, text=True, check=True)
            subprocess.run(["docker", "cp", model_path_host, f"{docker_id}:app/{model_path_container}"], capture_output=False, text=True, check=True)

            return docker_id

        except Exception as e:
            _log.write(f"Erreur lors de l'exécution de la commande Docker : {e}")
            return False

    def run_tf_container_main(self):
        try:
            process = subprocess.Popen(['docker', 'exec', super().get_docker_id(), 'python', 'main.py'],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                stdin=subprocess.DEVNULL,
                text=False,
            )

            return True
        except Exception as e:
            _log.write(f"Erreur lors de l'exécution de la commande Docker : {e}")
            return False

    def stop_tf_container(self, docker_instance_ids):
        try:
            docker_id = self.find_running_container(docker_instance_ids)

            model_path_host = f"./{self.config.get('model_path', 'models/')}{super().get_model_full_name()}"
            model_path_container = f"{self.config.get('model_path', 'models/')}"

            # copy two times the model to the container otherwise the model is not found...
            subprocess.run(["docker", "cp", f"{docker_id}:app/{model_path_container}", model_path_host], capture_output=True, text=True, check=True)
            subprocess.run(["docker", "cp", f"{docker_id}:app/{model_path_container}", model_path_host], capture_output=True, text=True, check=True)

            subprocess.run(['docker', 'stop', docker_id], capture_output=True, text=True, check=True)
            return True

        except Exception as e:
            _log.write(f"Erreur lors de l'exécution de la commande Docker : {e}")
            return False

    def find_running_container(self, docker_instance_ids):
        try:
            client = docker.from_env()
            running_containers = client.containers.list()
            running_container_ids = [container.id for container in running_containers]

            for container_id in docker_instance_ids:
                if container_id in running_container_ids:
                    return container_id

        except Exception as e:
            _log.write(f"Erreur lors de la recherche du conteneur : {e}")
            return False
