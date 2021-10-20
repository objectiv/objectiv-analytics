from flask import Flask, Response, make_response, request
from flask_cors import CORS

import psycopg2
import psycopg2.extras as extras

import os
import json
from typing import Dict
import uuid
import time

import pickle
import base64


_PG_HOSTNAME = os.environ.get('POSTGRES_HOSTNAME', 'localhost')
_PG_PORT = os.environ.get('POSTGRES_PORT', '5432')
_PG_DATABASE_NAME = os.environ.get('POSTGRES_DB', 'objectiv')
_PG_USER = os.environ.get('POSTGRES_USER', 'objectiv')
_PG_PASSWORD = os.environ.get('POSTGRES_PASSWORD', '')

dsn = f"dbname='{_PG_DATABASE_NAME}' user='{_PG_USER}' host='{_PG_HOSTNAME}' password='{_PG_PASSWORD}' port='{_PG_PORT}'"

# keep track of open connections
connections: Dict = {}


def serialize(data: Dict) -> str:
    serialized = pickle.dumps(data)
    encoded_bytes = base64.b64encode(serialized)
    return str(encoded_bytes, "utf-8")


def unserialize(data: str) -> Dict:
    return json.loads(data)


app = Flask(__name__)

CORS(app,
     resources={r'/*': {
         'origins': '*',
         'supports_credentials': True,  # needed for cookies
         # Setting max_age to a higher values is probably useless, as most browsers cap this time.
         # See https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Access-Control-Max-Age
         'max_age': 3600 * 24
     }})


@app.route("/")
def index():

    for h in request.headers:
        print(f'got header: {h}')

    return "hello"


@app.route("/connect", methods=["post"])
def db_connect() -> Response:
    result = {
        'connection_id': 0,
        'connected': False
    }
    try:
        conn = psycopg2.connect(dsn, cursor_factory=extras.DictCursor)
        connection_id = uuid.uuid4().urn

        connections[connection_id] = {
            "connection": conn,
            "time": time.time()
        }

        print(f'Created connection: {connection_id}')

        result['connection_id'] = connection_id
        result['connected'] = True

    except Exception as e:
        print(f'db is b0rken {e}')

    return make_response(serialize(result), 200, {"Content-Type": "application/json"})


@app.route("/disconnect", methods=["post"])
def db_disconnect() -> Response:
    raw_data = request.data

    data = unserialize(raw_data)
    connection_id = data['connection_id']

    try:
        _get_connection(connection_id).close()
    except Exception as e:
        print(f'couldnt find connection {connection_id} for disconnect {e}')

    if connection_id in connections:
        del connections[connection_id]

    print(f'Closed connection: {connection_id}')
    result = {'result': 'ok'}
    return make_response(serialize(result), 200, {"Content-Type": "application/json"})


def _get_connection(connection_id: str) :
    if connection_id in connections:
        print(f"returning connection {connection_id} -> {connections[connection_id]}")
        return connections[connection_id]['connection']
    raise Exception('Could not find connection')


@app.route("/query", methods=["post"])
def db_query() -> Response:
    raw_data = request.data
    print(f'trying to unserialize {raw_data}')
    data = unserialize(raw_data)

    if 'query' not in data:
        raise Exception('Not enough parameters')

    if 'connection_id' not in data:
        raise Exception('No connection specified')

    query = data['query']

    # run query an get resulting rows
    cur = _get_connection(connection_id=data['connection_id']).cursor()
    cur.execute(query)
    rows = cur.fetchall()

    # get description of result table columns
    column_fields = ('name', 'type_code', 'display_size', 'internal_size', 'precision', 'scale', 'null_ok', 'table_oid', 'table_column')
    description = []
    for column in cur.description:
        description.append([getattr(column, f) for f in column_fields if hasattr(column, f)])

    result = {
        'description': description,
        'rows': []
    }
    for row in rows:
        result['rows'].append({k: v for k, v in row.items()})

    print(f'got query: {query}')
    print(result)
    response = serialize(result)

    return make_response(response, 200, {"Content-type": "application/json"})


if __name__ == "__main__":
    app.run()


