#!/usr/bin/env python3

from classes.Log import log


class MasterClass:
    def __init__(self, data):
        super().__init__()

        self.user_id = data.get('user_id')
        self.model_name = data.get('model_name')
        self.in_docker = False
        self.docker_id = self.get_docker_internal_id()
        self.HOST = self.get_host()
        self.PORT = 3000  # 3000 for api server, 5000 for env server

    def get_user_id(self):
        return self.user_id
    
    def get_docker_id(self):
        return self.docker_id
    
    def set_docker_id(self, docker_id):
        self.docker_id = docker_id
    
    def get_model_name(self):
        return self.model_name
    
    def get_model_full_name(self):
        return f"{self.user_id}__{self.model_name}"

    def get_docker_internal_id(self):
        try:
            with open('/proc/self/cgroup', 'r') as cgroup_file:
                cgroup_content = cgroup_file.read()
                lines = cgroup_content.split('\n')
                for line in lines:
                    if 'docker' in line:
                        self.in_docker = True
                        return line.split('/')[-1]
        except Exception as e:
            log.write(f"Erreur lors de la récupération de l'ID du conteneur : {e}")

    def get_host(self):
        return 'http://host.docker.internal' if self.in_docker else 'http://127.0.0.1'
