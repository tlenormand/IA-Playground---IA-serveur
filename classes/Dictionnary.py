#!/usr/bin/env python3

import json


class Dictionnary:
    def __init__(self):
        self.errors_dictionary = self._load("config/errors.json")

    ############################################################################
    # Private methods
    ############################################################################

    def _load(self, path):
        """ Load dictionary from JSON file. """
        with open(path) as json_file:
            return json.load(json_file)

    ############################################################################
    # Public methods
    ############################################################################
