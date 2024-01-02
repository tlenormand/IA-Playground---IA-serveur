#!/usr/bin/env python3

from controllers.test_controller import test_get_controller
from controllers.docker_controller import create_docker_post_controller, get_model_docker_running_post_controller
from controllers.model_controller import create_model_post_controller, delete_model_post_controller, get_model_docker_post_controller
from controllers.atari_controller import train_atari_post_controller, stop_atari_post_controller, create_atari_post_controller, reset_atari_post_controller, step_atari_post_controller


functions = {
    'env/test': {
        'GET': test_get_controller
    },
    'env/model/create': {
        'POST': create_model_post_controller
    },
    'env/model/delete': {
        'POST': delete_model_post_controller
    },
    'env/dockers/create': {
        'POST': create_docker_post_controller
    },
    'env/dockers/get_model': {
        'POST': get_model_docker_post_controller
    },
    'env/dockers/running': {
        'POST': get_model_docker_running_post_controller
    },
    'env/atari/train/start': {
        'POST': train_atari_post_controller
    },
    'env/atari/train/stop': {
        'POST': stop_atari_post_controller
    },
    'env/atari/create': {
        'POST': create_atari_post_controller
    },
    'env/atari/reset': {
        'POST': reset_atari_post_controller
    },
    'env/atari/step': {
        'POST': step_atari_post_controller
    }
}
