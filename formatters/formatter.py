#!/usr/bin/env python3

from jsonschema import validate, ValidationError

from formatters.formatter_schemas import schema
from classes.Log import log


def formatter(endpoint, method, data):
    try:
        if endpoint in schema:
            if method in schema[endpoint]:
                validate(data, schema[endpoint][method])
                return True
            else:
                log.exception("formatterMethodNotFound", endpoint=endpoint, method=method)
        else:
            log.exception("formatterEndpointNotFound", endpoint=endpoint, method=method)
    except ValidationError as e:
        log.exception("formatterValidationError", endpoint=endpoint, method=method, error=e)
