#!/usr/bin/env python3

from jsonschema import validate, ValidationError

from formatters.formatter_schemas import schema
from classes._Logs import _log


def formatter(endpoint, method, data):
    try:
        if endpoint in schema:
            if method in schema[endpoint]:
                validate(data, schema[endpoint][method])
                return True
            else:
                raise Exception(f"Error in formatter: Method {method} of {endpoint} not found")
        else:
            raise Exception(f"Error in formatter: Endpoint {endpoint} not found")
    except ValidationError as e:
        _log.write(f"Validation error: {e}")
        return False
