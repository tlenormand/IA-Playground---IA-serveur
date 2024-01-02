#!/usr/bin/env python3

GAMES = {
    'All': {
        'inputs': {
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
        },
    },
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

PLAYERS = {}
