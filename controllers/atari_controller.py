#!/usr/bin/env python3

import numpy as np

from globals.global_variables import PLAYERS
from classes.Docker import Docker
from classes.Atari import Atari


def train_atari_post_controller(data):
    Docker_instance = Docker(data)
    docker_id = Docker_instance.run_tf_container()
    success = Docker_instance.run_tf_container_main()

    if not success:
        return {'success': False, 'message': 'Training failed'}

    return {'success': success, 'message': 'Training started', 'data': {
        'docker_id': docker_id
    }}
 
def stop_atari_post_controller(data):
    Docker_instance = Docker(data)
    Docker_instance.stop_tf_container(data.get('docker_instance_ids'))

    return {'success': True, 'message': 'Training stopped'}

def create_atari_post_controller(data):
    players_added = []

    for player in data['players']:
        print("player name::", player['name'])
        if player['name'] in PLAYERS:
            del player['name']

        player["user_id"] = data.get("user_id")
        player["model_name"] = data.get("model_name")

        print("player::", player)

        PLAYERS[player["name"]] = player
        print("PLAYERS::",PLAYERS)
        PLAYERS[player["name"]]['Atari_instance'] = Atari(player)

        state, info = PLAYERS[player["name"]]['Atari_instance'].reset()
        PLAYERS[player["name"]]['state'] = state

        players_added.append(player['name'])


    return { 'success': True,
        'message': f'{len(players_added)} players added: {players_added}'
    }

def reset_atari_post_controller(data):
    details = {}

    print("reset_atari_post_controller::", data)

    for player in data['players']:
        state, info = PLAYERS[player['name']]['Atari_instance'].reset()

        PLAYERS[player['name']]['state'] = state
        PLAYERS[player['name']]['reward'] = 0
        PLAYERS[player['name']]['done'] = False
        PLAYERS[player['name']]['info'] = info

        details[player['name']] = {
            'state': np.array(state).tolist(),
            'reward': 0,
            'done': False,
            'info': info
        }

    return {
        'success': True,
        'data': details
    }

def step_atari_post_controller(data):
    details = {}

    for player in data['players']:
        print("player name::", player)
        if PLAYERS.get(player['name'])['type'] == 'ia':
            state, reward, done, info = PLAYERS[player['name']]['Atari_instance'].ia_step()
        else:
            state, reward, done, info = PLAYERS[player['name']]['Atari_instance'].player_step(player['action'])

        PLAYERS[player['name']]['state'] = state
        PLAYERS[player['name']]['reward'] = reward
        PLAYERS[player['name']]['done'] = done
        PLAYERS[player['name']]['info'] = info

        details[player['name']] = {
            'state': np.array(state).tolist(),
            'reward': reward,
            'done': done,
            'info': info
        }

    return {
        'success': True,
        'data': details
    }