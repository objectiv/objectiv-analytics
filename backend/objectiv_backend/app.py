from flask import Flask
from flask_cors import CORS

from objectiv_backend.common.config import init_collector_config


def create_app() -> Flask:
    from objectiv_backend.end_points import collector
    from objectiv_backend.end_points import schema

    # load config - this will raise an error if there are configuration problems, and will cache the
    # result for later calls.
    init_collector_config()

    flask_app = Flask(__name__, static_folder=None)  # type: ignore
    flask_app.add_url_rule(rule='/schema', view_func=schema.schema, methods=['GET'])
    flask_app.add_url_rule(rule='/jsonschema', view_func=schema.json_schema, methods=['GET'])
    flask_app.add_url_rule(rule='/', view_func=collector.collect, methods=['POST'])
    init_cors(flask_app)
    return flask_app


def init_cors(app: Flask):
    """ Initialize the flask CORS plugin. """
    # We only have a single endpoint that ingests tracker data; the other endpoints only return data. We
    # are not afraid of any CSRF attacks, nor of people reusing our request-responses in other pages, and
    # we don't want to be strict in the origin of request. As such we don't have need for CORS protections,
    # and we can tell the browser to disable it altogether for this origin, coming from all origins.
    CORS(app,
         resources={r'/*': {
             'origins': '*',
             'supports_credentials': True,  # needed for cookies
             # Setting max_age to a higher values is probably useless, as most browsers cap this time.
             # See https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Access-Control-Max-Age
             'max_age': 3600 * 24
         }})


app = create_app()
