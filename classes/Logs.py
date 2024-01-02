#!/usr/bin/env python3

import time
import json
import requests

import numpy as np

from classes._Logs import _log
from tabulate import tabulate


class Logs:
    def __init__(self, data):
        self.config = self.init_data(data)
        self.config['is_in_docker'] = self.is_in_docker()
        self.config['docker_instance_id'] = self.get_docker_instance_id()
        self.log = {
            "docker_instance_id": self.config.get('docker_instance_id'),
            "program_execution_number": 0,
            "game_number_total": 0,
            "game_number_training": 0,
            "frame_count_total": 0,
            "frame_count_training": 0,
            "frame_count_game": 0,
            "executed_time_total": 0,
            "executed_time_training": 0,
            "executed_time_game": 0,
            "epsilon": 0,
            "action": 0,
            "action_type": '',
            "reward": 0,
            "reward_game": 0,
            "reward_training": 0,
            "new_model": False,
            "done": False,
        }
        self.logs_history = []
        self.start_time = time.time()
        self.intermediate_time = self.start_time

    def init_data(self, data):
        return {
            'period_display': 100,
            'can_save_logs': False,
            'can_send_logs': False,
            **data.get('logs_config')
        }

    def display(self):
        if self.log.get('frame_count_total') % self.config.get('period_display') != 0 and not self.log.get('done') and not self.log.get('new_model') and not self.log.get('reward'):
            return

        # Create a list of key-value pairs from self.log, rounding the values to 6 decimal places if they are of float type
        table_data = [[key, value if not isinstance(value, float) else round(value, 6)] for key, value in self.log.items()]
        # Transpose the list of key-value pairs to display the data in columns, not rows
        table_data = list(map(list, zip(*table_data)))
        # Use the 'tabulate' library to format the data as a pipe-separated table
        table = tabulate(table_data, tablefmt='pipe')
        _log.write(table)

    def push(self):
        executed_time = time.time() - self.intermediate_time
        self.intermediate_time = time.time()

        self.log['frame_count_total'] += 1
        self.log['frame_count_game'] += 1
        self.log['frame_count_training'] += 1
        self.log['executed_time_total'] += executed_time
        self.log['executed_time_game'] += executed_time
        self.log['executed_time_training'] += executed_time

        self.logs_history.append(self.log.copy())

        self.display()

        # reset unique values
        self.log['new_model'] = False
        self.log['done'] = False

    def is_in_docker(self):
        """ Check if the program is running in a docker container """
        with open('/proc/1/cgroup', 'rt') as ifh:
            return 'docker' in ifh.read()

    def get_docker_instance_id(self):
        if self.config.get('is_in_docker'):
            with open('/proc/self/cgroup', 'rt') as ifh:
                return ifh.read().splitlines()[-1].split('/')[-1]

    def send(self, logs_type=None):
        """ Send logs to the server """
        data = None
        params = None

        # in docker use: HOST = 'http://host.docker.internal' otherwise use: HOST = 'http://0.0.0.0' or 'http://127.0.0.1'
        HOST = 'http://host.docker.internal' if self.config.get('is_in_docker') else 'http://127.0.0.1'
        PORT = 3000

        if logs_type == 'init':
            params = { 'type': 'init' }
            data = self.encode_logs({
                'dockerInstanceId': self.dockerInstanceId,
                'model': self.model,
                'modelConfig': self.modelConfig,
                'modelLayers': self.modelLayers,
            })
            url = f"{HOST}:{PORT}/api/models/create"
        else:
            params = { 'type': 'logs' }
            data = self.encode_logs()
            url = f"{HOST}:{PORT}/api/logs/create"

        try:
            response = requests.post(
                url,
                data=json.dumps(data),
                headers={'Content-Type': 'application/json'},
                params=params
            )

            if response.status_code != 200:
                _log(f"Échec de l'envoi des logs. Code de réponse: {response.status_code}")

        except Exception as e:
            _log(f"Erreur lors de l'envoi des logs. url: {url} - error: {e}")

    def encode_logs(self, data=None):
        """ Encode les logs pour les rendre sérialisables en JSON.

        Args:
            logs (dict): Les logs à encoder.

        Returns:
            str: Une chaîne JSON encodée.
        """
        if data is None:
            data = self.log

        def convert_to_json_serializable(obj):
            if isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            else:
                return obj

        # Convertir les valeurs non sérialisables
        logs_serializable = {key: convert_to_json_serializable(value) for key, value in data.items()}

        return logs_serializable
