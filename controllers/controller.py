#!/usr/bin/env python3

from classes._Controller import Controller
from controllers.controller_functions import functions


Controller = Controller()

def controller(endpoint, method, data):
    return Controller.map(endpoint, method, functions, data)
