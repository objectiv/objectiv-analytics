import datetime
import json
from io import StringIO, BytesIO

import flask
import time
from typing import List, Tuple, Optional
import os
import uuid

import boto3
from botocore.exceptions import ClientError
from flask import Flask, request, Response, Request
from flask_cors import CORS

from objectiv_backend.common.db import get_db_connection
from objectiv_backend.common.event_utils import event_add_construct_context, add_global_context_to_event
from objectiv_backend.common.types import EventWithId, EventData, ContextData
from objectiv_backend.schema.validate_events import validate_structure_event_list
from objectiv_backend.workers.pg_queues import PostgresQueues, ProcessingStage
from objectiv_backend.workers.pg_storage import insert_events_into_nok_data
from objectiv_backend.workers.worker_enrichment import process_events_enrichment
from objectiv_backend.workers.worker_entry import process_events_entry
from objectiv_backend.workers.worker_finalize import insert_events_into_data

app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*", "supports_credentials": True}})

# Where to store the output JSONs
JSON_DIR: Optional[str] = os.environ.get('JSON_DIR', None)

# AWS settings
AWS_REGION = 'eu-west-1'  # default region is Ireland
# default access keys to an empty string, otherwise the boto library will default ot user defaults.
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID', '')  # Need an IAM user with read/write access to S3 bucket
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY', '')  # Need an IAM user with read/write access to S3
AWS_BUCKET = 'obj-tracker-journeys'
AWS_S3_PREFIX = os.environ.get('AWS_S3_PREFIX', 'test-prefix')

# Whether to run in sync mode (default) or async-mode.
ASYNC_MODE = os.environ.get('ASYNC_MODE', '') == 'true'

# set to False to disable setting a session cookie
OBJ_COOKIE = 'obj_user_id'
OBJ_COOKIE_DURATION = 60 * 60 * 24 * 365 * 5

# Some limits on the inputs we accept
DATA_MAX_SIZE_BYTES = 1_000_000
DATA_MAX_EVENT_COUNT = 1_000


@app.route('/', methods=['POST'])
def index() -> Response:
    current_millis = round(time.time() * 1000)
    try:
        events = _get_event_data(flask.request)
    except ValueError as exc:
        print(f'Data problem: {exc}')  # todo: real error logging
        # Todo: write data to not okay data directory?
        return _get_response(error_count=1, event_count=-1)

    # Do all the enrichment steps that can only be done in this phase
    add_http_contexts(events)
    add_cookie_id_contexts(events)
    set_time_in_events(events, current_millis)

    events_with_id = [EventWithId(id=uuid.uuid4(), event=event) for event in events]
    ok_events, nok_events = write_events_db(events_with_id)

    write_events_to_disk_and_s3(ok_events=ok_events, nok_events=nok_events)

    return _get_response(error_count=len(nok_events), event_count=len(events))


def _get_event_data(request: Request) -> List[EventData]:
    """
    Parse the requests data as json and return as a list

    :raise ValueError:
        1) data is not valid json
        2) data is bigger than DATA_MAX_SIZE_BYTES
        3) The parsed data is a list with more than DATA_MAX_EVENT_COUNT entries
        4) The parsed data is not a list, as expected
        5) The parsed data is not structured as a list of events. This only does basic validation, see
            the validate_structure_data function for more information
    :param request: Request from which to parse the data
    :return: the parsed data, a list of EventData
    """
    post_data = request.data
    if len(post_data) > DATA_MAX_SIZE_BYTES:
        # if it's more than a megabyte, we'll refuse to process
        raise ValueError(f'Data size exceeds limit')
    events = json.loads(post_data)
    if not isinstance(events, list):
        raise ValueError('Parsed data is not a list')
    if len(events) > DATA_MAX_EVENT_COUNT:
        raise ValueError('Events exceeds limit')
    error_info = validate_structure_event_list(event_data=events)
    if error_info:
        raise ValueError(f'List of Events not structured well: {error_info[0].info}')
    return events


def _get_response(error_count: int, event_count: int) -> Response:
    """ Create a Response object, with json content, and a cookie set if needed. """
    status = 200 if error_count == 0 else 400
    msg = json.dumps({
        "status": f"{status}",
        "error_count": error_count,
        "event_count": event_count
    })
    response = Response(mimetype='application/json', status=status, response=msg)
    if OBJ_COOKIE:
        cookie_id = _get_cookie_id()
        response.set_cookie(key=OBJ_COOKIE, value=f'{cookie_id}', max_age=OBJ_COOKIE_DURATION, samesite='Lax')
    return response


def _get_cookie_id() -> str:
    """
    Get the tracking cookie uuid from the current request.
    If no tracking cookie is present in the current request, a random uuid is generated.
    The generated random uuid is stored, so multiple invocations of this function within a request will
    return the same value.
    """
    cookie_id = request.cookies.get(OBJ_COOKIE)
    if not cookie_id:
        # There's no cookie in the request, perhaps we already generated one earlier in this request
        cookie_id = flask.g.get('G_COOKIE_ID')

    if not cookie_id:
        # There's no cookie in the request, and we have not yet generated one
        # use uuid4 (random), so there is no predictability and bad actors cannot ruin sessions of others
        cookie_id = uuid.uuid4()
        flask.g.G_COOKIE_ID = cookie_id
        print(f'Generating cookie_id: {cookie_id}')

    return str(cookie_id)


def add_http_contexts(events: List[EventData]):
    """
    Modify the given list of events: Add the HttpContext to each event
    """
    # get http context for current request (same for all events in this request)
    http_context = _get_http_context()
    for event in events:
        add_global_context_to_event(event=event, context=http_context)


def add_cookie_id_contexts(events: List[EventData]):
    """
    Modify the given list of events: Add the CookieIdContext to each event, if cookies are enabled.
    """
    if not OBJ_COOKIE:
        return
    cookie_id = _get_cookie_id()
    for event in events:
        event_add_construct_context(
            event=event,
            context_type='CookieIdContext',
            context_id=cookie_id,
            cookie_id=cookie_id
        )


def set_time_in_events(events: List[EventData], current_millis: int):
    """
    Modify the given list of events: Set the correct time in the events

    1. Validate that - Note: currently failing this validation has no consequences
      1.1. All events in the list are in chronological order:
      1.2. The events are not more that X seconds delayed.
    2. Adjust time if needed: if the current requests header has an X-timestamp header, we'll use that to
       calculate the client's clock skew, and adjust all events in the list.
    :param events: List of events to modify
    :param current_millis: time in milliseconds since epoch UTC, when this request was received.
    """
    offset = 0
    if 'X-timestamp' in flask.request.headers:
        try:
            client_millis = int(flask.request.headers['X-timestamp'])
        except ValueError as exc:
            client_millis = current_millis
        offset = current_millis - client_millis
        print(f'debug - time offset: {offset}')
    for event in events:
        # event['time'] = event['time'] + offset
        # use current_millis as a fallback until time is implemented in the FE and made a required field.
        event['time'] = event.get('time', current_millis) + offset
    # Validate
    for event in events:
        MAX_DELAYED_EVENTS_MILLIS = 1000 * 3600  # TODO: move, different value?
        if (current_millis - event['time']) > MAX_DELAYED_EVENTS_MILLIS:
            pass
            #TODO: error?
    for i, event in enumerate(events):
        if i > 0 and events[i - 1]['time'] > event['time']:
            print(f'Events not in right order!!! timestamp {events[i - 1]["time"]} before {event["time"]}')
            # TODO: error?


def _get_http_context() -> ContextData:
    """ Create an HttpContext based on the data in the current request. """
    allowed_headers = ['Host', 'Origin', 'Referer', 'User-Agent']
    http_context = {}
    if request.remote_addr:
        http_context['remote_addr'] = request.remote_addr

    for h, v in request.headers.items():
        if h in allowed_headers:
            http_context[h.lower()] = v

    http_context['_context_type'] = 'HttpContext'
    http_context['id'] = 'http_context'
    return http_context


def write_events_db(events: List[EventWithId]) -> Tuple[List[EventWithId], List[EventWithId]]:
    """
    Write events to the database.
    * If not ASYNC_MODE (=default): All events are fully processed, and written to the final data table.
    * If ASYNC_MODE: All events are written to the entry queue. Workers will have to take care of
        further processing from there on. In this case all events are always returned as being OK, since
        the validation doesn't happen in this function.
    :param events: List of events, with assigned unique-ids
    :return: Tuple with two lists:
        ok events: events that were processed okay
        nok events: events that failed validation.
    """
    connection = get_db_connection()
    try:
        with connection:
            if ASYNC_MODE:
                pg_queue = PostgresQueues(connection=connection)
                pg_queue.put_events(queue=ProcessingStage.ENTRY, events=events)
                return events, []
            else:
                ok_events, nok_events = process_events_entry(events=events)
                print(f'ok_events: {len(ok_events)}, nok_events: {len(nok_events)}')
                insert_events_into_nok_data(connection, events=nok_events)
                ok_events = process_events_enrichment(events=ok_events)
                insert_events_into_data(connection, events=ok_events)
                return ok_events, nok_events
    finally:
        connection.close()


def write_events_to_disk_and_s3(ok_events: List[EventWithId], nok_events: List[EventWithId]) -> None:
    # TODO: do we need this?
    if ok_events:
        filename = f'OK/{time.time()}.json'
        data = _events_to_json(ok_events)
        _write_data_to_disk(data=data, filename=filename)
        _write_data_to_s3(data=data, filename=filename)
    if nok_events:
        filename = f'NOK/{time.time()}.json'
        data = _events_to_json(nok_events)
        _write_data_to_disk(data=data, filename=filename)
        _write_data_to_s3(data=data, filename=filename)


def _events_to_json(events: List[EventWithId]) -> str:
    result = []
    for event in events:
        # add newline so we can use this as raw input to AWS Athena
        json_str = json.dumps(event.event) + "\n"
        result.append(json_str)
    return ''.join(result)


def _write_data_to_disk(data: str, filename: str) -> None:
    if not JSON_DIR:
        print('Not storing on disk.')
        return
    path = f'{JSON_DIR}/{filename}'
    with open(path, 'w') as of:
        of.write(data)


def _write_data_to_s3(data: str, filename: str) -> None:
    if not AWS_ACCESS_KEY_ID or not AWS_SECRET_ACCESS_KEY:
        print('Not uploading to S3, access keys not specified.')
        return
    file_obj = BytesIO(data.encode('utf-8'))
    s3_client = boto3.client(
        service_name='s3',
        region_name=AWS_REGION,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
    try:
        dt = datetime.datetime.today()
        timestamp = dt.strftime('%Y/%m/%d')
        object_name = f'{AWS_S3_PREFIX}/{timestamp}/{filename}'
        s3_client.upload_fileobj(file_obj, AWS_BUCKET, object_name)
    except ClientError as e:
        print(f'Error uploading to s3: {e} ')
