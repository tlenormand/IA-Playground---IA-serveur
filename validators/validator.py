#!/usr/bin/env python3

from jsonschema import validate, ValidationError

from validators.validator_schemas import schema
from classes._Logs import _log


def validator(request):
    if request.method not in ['POST', 'PUT', 'PATCH']:
        return True

    endpoint = request.path[1:]  # Remove leading slash

    try:
        if endpoint in schema:
            if request.method in schema[endpoint]:
                validate(request.get_json(), schema[endpoint][request.method])
                return True
            else:
                raise Exception(f"Error in validator: Method {request.method} of {endpoint} not found")
        else:
            raise Exception(f"Error in validator: Endpoint {endpoint} not found")
    except ValidationError as e:
        _log.write(f"Validation error: {e}")
        return False
