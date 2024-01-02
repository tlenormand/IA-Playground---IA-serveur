#!/usr/bin/env python3

import numpy as np


class Games:
    def __init__(self, game):
        self.game = game
        self.actions = {
            0: 'NOOP',
            1: 'FIRE',
            2: 'UP',
            3: 'RIGHT',
            4: 'LEFT',
            5: 'DOWN',
            6: 'UPRIGHT',
            7: 'UPLEFT',
            8: 'DOWNRIGHT',
            9: 'DOWNLEFT',
            10: 'UPFIRE',
            11: 'RIGHTFIRE',
            12: 'LEFTFIRE',
            13: 'DOWNFIRE',
            14: 'UPRIGHTFIRE',
            15: 'UPLEFTFIRE',
            16: 'DOWNRIGHTFIRE',
            17: 'DOWNLEFTFIRE'
        }
        self.games = {
            'Breakout-v5': {
                'inputs': {
                    0: 0,
                    1: 1,
                    2: 3,
                    3: 4,
                },
            },
            "Assault-v5": {
                'inputs': {
                    0: 0,
                    1: 1,
                    2: 2,
                    3: 3,
                    4: 4,
                    5: 11,
                    6: 12,
                },
            },
        }

    def get_inputs_for_game(self):
        game = self.games.get(self.game)
        return game.get('inputs')

    def output_to_actions(self, output):
        game = self.games.get(self.game)
        inputs = game.get('inputs')
        return inputs.get(output)

    def action_to_output(self, action):
        game = self.games.get(self.game)
        inputs = game.get('inputs')
        print("output::", inputs)
        for key, value in inputs.items():
            print("key111::", key, action, value)
            if value == action:
                print("key::", key)
                return key

    def get_random_action(self):
        game = self.games.get(self.game)
        inputs = game.get('inputs')
        return np.random.choice(list(inputs.keys()))
