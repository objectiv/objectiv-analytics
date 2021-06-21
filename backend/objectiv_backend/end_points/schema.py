"""
Copyright 2021 Objectiv B.V.
"""
import json

from flask import Response

from objectiv_backend.common.config import get_collector_config
from objectiv_backend.end_points.common import get_json_response
from objectiv_backend.schema.generate_json_schema import generate_json_schema


def schema() -> Response:
    """ Endpoint that returns the event schema in our own notation. """
    event_schema = get_collector_config().schema
    msg = str(event_schema)
    return get_json_response(status=200, msg=msg)


def json_schema() -> Response:
    """ Endpoint that returns a jsonschema that describes the event schema. """
    event_schema = get_collector_config().schema
    msg = json.dumps(generate_json_schema(event_schema), indent=4)
    return get_json_response(status=200, msg=msg)
