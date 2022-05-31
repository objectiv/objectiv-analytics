import uuid
import os

from flask import Flask, Response, Request
import flask
from flask_cors import CORS
import json


import semver
import requests

from typing import Generator, Dict
import time

from objectiv_backend.schema.schema import make_event_from_dict, AbstractEvent

# url to objectiv tracker
TRACKER_URL = os.environ.get('OBJECTIV_TRACKER_URL', 'http://localhost:8081')

# base url to PYPI index, use localhost for local proxy cache
PYPI_BASE_URL = os.environ.get('OBJECTIV_PYPI_BASE_URL', 'http://localhost')


def get_current_version(package: str) -> str:
    """
    Query PyPi index to find latest version of package
    :param package: str - name of pacahe
    :return: str - version if available
    """

    url = f'{PYPI_BASE_URL}/pypi/{package}/json'
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.get(url=url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        if 'info' in data and 'version' in data['info']:
            # only return version if everything went OK, otherwise, too bad!
            return data['info']['version']

    return None


def parse_payload(request: Request) -> Generator:
    """
    Parse Post payload, should be of the form package:version
    :param request: Request object
    :return: Generator with list (if any) of packages and version
    """
    payload = request.data.decode('utf-8')
    for line in payload.split('\n'):

        terms = line.split(':')
        if len(terms) > 1:
            yield {
                'name': terms[0].strip(),
                'version': terms[1].strip()
            }


def check_version() -> Response:
    """
    Process incoming version check request:
    - parse package names and versions from request
    - query pypi (cache) for current versions
    - compare, and create response
    :return:Response object
    """
    # we only check our own packages, other packages will be ignored
    packages_to_check = ['objectiv-modelhub']

    request: Request = flask.request
    data = parse_payload(request)
    packages = {}
    if data:
        for package in data:
            if package['name'] not in packages_to_check:
                continue
            current_version = get_current_version(package=package['name'])

            try:
                update_available = semver.compare(current_version, package['version']) > 0
                packages[package['name']] = {
                        'update': update_available,
                        'current_version': current_version,
                        'local_version': package['version']}
            except ValueError:
                # this happens if the provided version is invalid
                pass

    if packages:
        # only try to track if this request contains a valid payload
        event = make_event()
        try:
            user_agent = str(request.user_agent)

            for package in packages:
                if package == 'objectiv-modelhub':
                    version = packages[package]['local_version']
                    user_agent += f' {package}/{version}'
            track_event(event, user_agent)

        except requests.exceptions.RequestException as re:
            # this shouldn't happen, but we continue, as we can still return version info
            print(f'Could not send event: {re}')
    else:
        print('error:Could not process request')

    response = []
    docs_url = 'https://objectiv.io/docs/modeling/open-model-hub/version-check/'
    for package in packages:
        # format response, containing package, update status, version, and message
        update = packages[package]['update']
        current_version = packages[package]['current_version']

        message = f'New version {current_version} of {package} available. Upgrade to get the latest pre-built ' \
                  f'models & Bach operations: `pip install --upgrade {package}`. See more at {docs_url}'

        response.append(f'{package}:{update}:{current_version}:{message}')

    return Response(mimetype='application/text', status=200, response='\n'.join(response))


def make_event() -> AbstractEvent:
    """
    Create valid event to push to collector
    :return: AbstractEvent
    """
    event_data = {
        '_type': 'ApplicationLoadedEvent',
        'id': str(uuid.uuid4()),
        'global_contexts': [
            {
                '_type': 'ApplicationContext',
                'id': 'BachVersionChecker'
            }
        ],
        'location_stack': [],
        'time': int(time.time()*1000)
    }
    return make_event_from_dict(event_data)


def track_event(event: AbstractEvent, user_agent: str):
    """
    Post event to collector
    :param event: AbstractEvent - event to be sent to collector
    :param user_agent: str - user agent to use in request
    :return: None
    """

    headers = {
        'Content-Type': 'application/json',
        'User-agent': user_agent
    }
    data = {
        'events': [event],
        'transport_time': int(time.time()*1000)
    }
    requests.post(TRACKER_URL, data=json.dumps(data), headers=headers)


def create_app() -> Flask:

    flask_app = flask.Flask(__name__, static_folder=None)  # type: ignore
    flask_app.add_url_rule(rule='/check_version', view_func=check_version, methods=['POST'])
    CORS(flask_app,
         resources={r'/*': {
             'origins': '*',
             # Setting max_age to a higher values is probably useless, as most browsers cap this time.
             # See https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Access-Control-Max-Age
             'max_age': 3600 * 24
         }})
    return flask_app


app = create_app()
