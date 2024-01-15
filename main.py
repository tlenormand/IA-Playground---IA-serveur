#!/usr/bin/env python3

import os

from classes.Atari import Atari


def get_env():
    return {
        'user_id': os.getenv('USER_ID'),
        'model_name': os.getenv('MODEL_NAME'),
        'model_config': {
            'can_load_model': os.getenv('CAN_LOAD_MODEL'),
            'model_path': os.getenv('MODEL_PATH'),
            'can_save_model': bool(os.getenv('CAN_SAVE_MODEL'))
        },
        'atari_config': {
            'game': os.getenv('GAME'),
            'epsilon_min': float(os.getenv('EPSILON_MIN')),
            'epsilon': float(os.getenv('EPSILON')),
            'can_render': bool(os.getenv('CAN_RENDER')),
            'can_train': bool(os.getenv('CAN_TRAIN')),
        },
        'logs_config': {
            'can_save_logs': bool(os.getenv('CAN_SAVE_LOGS')),
            'can_send_logs': bool(os.getenv('CAN_SEND_LOGS')),
        },
        'docker_config': {
            'can_containerize': bool(os.getenv('CAN_CONTAINERIZE'))
        },

        ############################################################################################################
        # FOR LOCAL TESTING
        ############################################################################################################
        # 'user_id': "testUser",
        # 'model_name': "test",
        # 'model_config': {
        #     'can_load_model': True,
        #     'model_path': "models/",
        #     'can_save_model': True
        # },
        # 'atari_config': {
        #     'game': "Breakout-v5",
        #     'epsilon_min': 0.1,
        #     'epsilon': 1,
        # },
        # 'logs_config': {
        #     'can_save_logs': True,
        #     'can_send_logs': True,
        # },
        # 'docker_config': {
        #     'can_containerize': True,
        # },
        # 'can_containerize': False,
        # 'can_train': True,
        # 'can_render': False,
    }

def main():
    Atari_instance = Atari(get_env())
    Atari_instance.train()

if __name__ == "__main__":
    main()
