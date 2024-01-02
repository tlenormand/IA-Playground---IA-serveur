#!/usr/bin/env python3

class Controller:
    def __init__(self):
        pass

    def map(self, endpoint, method, functions, data):
        if endpoint in functions:
            if method in functions[endpoint]:
                return functions[endpoint][method](data)
            else:
                return {'success': False, 'message': 'Method not found'}, 404

        return {'success': False, 'message': f'Error in controller: Endpoint {endpoint} not found'}, 404
