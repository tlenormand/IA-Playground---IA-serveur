#!/usr/bin/env python3

import configparser


def set_env_from_file(file):
    config = configparser.ConfigParser()
    config.read(file)
    env = {}

    for option, value in config['DEFAULT'].items():
        env[option] = value

    return env
