"""
Copyright 2021 Objectiv B.V.
"""
import uuid
import flask
from flask import Response
from objectiv_backend.common.config import get_collector_config


def get_json_response(status: int, msg: str) -> Response:
    """
    Create a Response object, with json content, and a cookie set if needed.
    :param status: http status code
    :param msg: valid json string
    """
    response = Response(mimetype='application/json', status=status, response=msg)

    cookie_config = get_collector_config().cookie
    if cookie_config:
        cookie_id = get_cookie_id()
        response.set_cookie(key=cookie_config.name, value=f'{cookie_id}',
                            max_age=cookie_config.duration, samesite='Lax')
    return response


def get_cookie_id() -> str:
    """
    Get the tracking cookie uuid from the current request.
    If no tracking cookie is present in the current request, a random uuid is generated.
    The generated random uuid is stored, so multiple invocations of this function within a request will
    return the same value.

    :raise Exception: If cookies are not configured
    """
    cookie_config = get_collector_config().cookie
    if not cookie_config:
        raise Exception('Cookies are not configured')  # This is a bug. We shouldn't call this function.
    cookie_id = flask.request.cookies.get(cookie_config.name)
    if not cookie_id:
        # There's no cookie in the request, perhaps we already generated one earlier in this request
        cookie_id = flask.g.get('G_COOKIE_ID')

    if not cookie_id:
        # There's no cookie in the request, and we have not yet generated one
        # use uuid4 (random), so there is no predictability and bad actors cannot ruin sessions of others
        cookie_id = str(uuid.uuid4())
        flask.g.G_COOKIE_ID = cookie_id
        print(f'Generating cookie_id: {cookie_id}')

    return str(cookie_id)
