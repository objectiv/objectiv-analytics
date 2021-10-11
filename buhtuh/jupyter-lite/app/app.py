from flask import Flask, make_response, request
from flask_cors import CORS

import psycopg2, psycopg2.extras as extras
import os
import json 
import datetime
import decimal
from typing import Dict

_PG_HOSTNAME = os.environ.get('POSTGRES_HOSTNAME', 'localhost')
_PG_PORT = os.environ.get('POSTGRES_PORT', '5432')
_PG_DATABASE_NAME = os.environ.get('POSTGRES_DB', 'objectiv')
_PG_USER = os.environ.get('POSTGRES_USER', 'objectiv')
_PG_PASSWORD = os.environ.get('POSTGRES_PASSWORD', '')

dsn = f"dbname='{_PG_DATABASE_NAME}' user='{_PG_USER}' host='{_PG_HOSTNAME}' password='{_PG_PASSWORD}' port='{_PG_PORT}'"

try:
    conn = psycopg2.connect(dsn, cursor_factory=extras.DictCursor)
except Exception as e:
    print(f'db is b0rken {e}')
    exit(1)
cur = conn.cursor()

class MyEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, (datetime.datetime, datetime.date, datetime.time)):
            return obj.isoformat()
        elif isinstance(obj, datetime.timedelta):
            return (datetime.datetime.min + obj).time().isoformat()
        elif isinstance(obj, decimal.Decimal):
            return float(obj)
        return super(MyEncoder, self).default(obj)

def json_encode(data: Dict) -> str:
    encoder = MyEncoder()
    return encoder.encode(data)

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

@app.route("/query", methods=["post"])
def query():
    raw_data = request.data
    
    data = json.loads(raw_data)
    query = data['query']
    
    cur.execute(query)
    rows = cur.fetchall()
    
    result = []
    for row in rows:
        result.append({k:v for k,v in row.items()})
    

    print(f'got query: {query}')
    response = json_encode(result)
    print(f'sending result: {response}')

    return make_response(response, 200, {"Content-type": "application/json"})


if __name__ == "__main__":
    app.run()


