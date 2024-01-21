#!/usr/bin/env python3

from jsonschema import validate, ValidationError

from validators.validator_schemas import schema
from classes.Log import log


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
                log.exception("validatorMethodNotFound", endpoint=endpoint, method=request.method)
        else:
            log.exception("validatorEndpointNotFound", endpoint=endpoint, method=request.method)
    except ValidationError as e:
        log.exception("validatorValidationError", endpoint=endpoint, method=request.method, error=e)
        log.write(f"Validation error: {e}")
        return False
