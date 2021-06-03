import json
from datetime import datetime
from io import BytesIO

import flask
import time
from typing import List
import uuid

import boto3
from botocore.exceptions import ClientError
from flask import Flask, Response, Request
from flask_cors import CORS

from objectiv_backend.common.config import get_collector_config
from objectiv_backend.common.db import get_db_connection
from objectiv_backend.common.event_utils import event_add_construct_context, add_global_context_to_event
from objectiv_backend.common.types import EventWithId, EventData, ContextData
from objectiv_backend.schema.generate_json_schema import generate_json_schema
from objectiv_backend.schema.validate_events import validate_structure_event_list
from objectiv_backend.workers.pg_queues import PostgresQueues, ProcessingStage
from objectiv_backend.workers.pg_storage import insert_events_into_nok_data
from objectiv_backend.workers.worker_entry import process_events_entry
from objectiv_backend.workers.worker_finalize import insert_events_into_data

app = Flask(__name__)

# We only have a single endpoint that ingests tracker data. We are not afraid of any CSRF attacks, nor of
# people reusing our request-responses in other pages, and we don't want to be strict in the origin of
# request. As such we don't have need for CORS protections, and we can tell the browser to disable it
# altogether for this origin, coming from all origins.
cors = CORS(app,
            resources={r'/*': {
                'origins': '*',
                'supports_credentials': True,       # needed for cookies
                # Setting max_age to a higher values is probably useless, as most browsers cap this time.
                # See https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Access-Control-Max-Age
                'max_age': 3600 * 24
            }})


# Some limits on the inputs we accept
DATA_MAX_SIZE_BYTES = 1_000_000
DATA_MAX_EVENT_COUNT = 1_000


@app.route('/schema', methods=['GET'])
def schema() -> Response:
    event_schema = get_collector_config().schema
    msg = str(event_schema)
    return _get_json_response(status=200, msg=msg)


@app.route('/jsonschema', methods=['GET'])
def jsonschema() -> Response:
    event_schema = get_collector_config().schema
    msg = json.dumps(generate_json_schema(event_schema), indent=4)
    return _get_json_response(status=200, msg=msg)


@app.route('/', methods=['POST'])
def index() -> Response:
    current_millis = round(time.time() * 1000)
    try:
        events = _get_event_data(flask.request)
    except ValueError as exc:
        print(f'Data problem: {exc}')  # todo: real error logging
        return _get_collector_response(error_count=1, event_count=-1)

    # Do all the enrichment steps that can only be done in this phase
    add_http_contexts(events)
    add_cookie_id_contexts(events)
    set_time_in_events(events, current_millis)

    events_with_id = [EventWithId(id=uuid.uuid4(), event=event) for event in events]

    if not get_collector_config().async_mode:
        ok_events, nok_events = process_events_entry(events=events_with_id)
        print(f'ok_events: {len(ok_events)}, nok_events: {len(nok_events)}')
        write_sync_events(ok_events=ok_events, nok_events=nok_events)
        return _get_collector_response(error_count=len(nok_events), event_count=len(events))
    else:
        write_async_events(events=events_with_id)
        return _get_collector_response(error_count=0, event_count=len(events))


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


def _get_collector_response(error_count: int, event_count: int) -> Response:
    """
    Create a Response object, with a json message with event counts, and a cookie set if needed.
    """
    status = 200 if error_count == 0 else 400
    msg = json.dumps({
        "status": f"{status}",
        "error_count": error_count,
        "event_count": event_count
    })
    return _get_json_response(status=status, msg=msg)


def _get_json_response(status: int, msg: str) -> Response:
    """
    Create a Response object, with json content, and a cookie set if needed.
    :param status: http status code
    :param msg: valid json string
    """
    response = Response(mimetype='application/json', status=status, response=msg)

    cookie_config = get_collector_config().cookie
    if cookie_config:
        cookie_id = _get_cookie_id()
        response.set_cookie(key=cookie_config.name, value=f'{cookie_id}',
                            max_age=cookie_config.duration, samesite='Lax')
    return response


def _get_cookie_id() -> str:
    """
    Get the tracking cookie uuid from the current request.
    If no tracking cookie is present in the current request, a random uuid is generated.
    The generated random uuid is stored, so multiple invocations of this function within a request will
    return the same value.
    """
    cookie_config = get_collector_config().cookie
    cookie_id = flask.request.cookies.get(cookie_config.name)
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
    cookie_config = get_collector_config().cookie
    if not cookie_config:
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
    if flask.request.remote_addr:
        http_context['remote_addr'] = flask.request.remote_addr

    for h, v in flask.request.headers.items():
        if h in allowed_headers:
            http_context[h.lower()] = v

    http_context['_context_type'] = 'HttpContext'
    http_context['id'] = 'http_context'
    return http_context


def write_sync_events(ok_events: List[EventWithId], nok_events: List[EventWithId]):
    """
    Write the events to the following sinks, if configured:
        * postgres
        * aws
        * file system
    """
    output_config = get_collector_config().output
    if output_config.postgres:
        connection = get_db_connection(output_config.postgres)
        try:
            with connection:
                insert_events_into_data(connection, events=ok_events)
                insert_events_into_nok_data(connection, events=nok_events)
        finally:
            connection.close()

    if not output_config.file_system and not output_config.aws:
        return
    for prefix, events in ('OK', ok_events), ('NOK', nok_events):
        if events:
            data = _events_to_json(events)
            moment = datetime.utcnow()
            _write_data_to_fs_if_configured(data=data, prefix=prefix, moment=moment)
            _write_data_to_s3_if_configured(data=data, prefix=prefix, moment=moment)


def write_async_events(events: List[EventWithId]):
    """
    Write the events to the following sinks, if configured:
        * postgres - To the entry queue
        * aws - to the 'RAW' prefix
        * file system - to the 'RAW' directory
    """
    output_config = get_collector_config().output
    if output_config.postgres:
        connection = get_db_connection(output_config.postgres)
        try:
            with connection:
                pg_queue = PostgresQueues(connection=connection)
                pg_queue.put_events(queue=ProcessingStage.ENTRY, events=events)
        finally:
            connection.close()

    if not output_config.file_system and not output_config.aws:
        return
    prefix = 'RAW'
    if events:
        data = _events_to_json(events)
        moment = datetime.utcnow()
        _write_data_to_fs_if_configured(data=data, prefix=prefix, moment=moment)
        _write_data_to_s3_if_configured(data=data, prefix=prefix, moment=moment)


def _events_to_json(events: List[EventWithId]) -> str:
    """
    Convert list of events to a string with on each line a json object representing a single event.
    Note that the returned string is not a json list; This format makes it suitable as raw input to AWS
    Athena.
    """
    result = []
    for event in events:
        json_str = json.dumps(event.event) + "\n"
        result.append(json_str)
    return ''.join(result)


def _write_data_to_fs_if_configured(data: str, prefix: str, moment: datetime) -> None:
    """
    Write data to disk, if file_system output is configured.
    """
    fs_config = get_collector_config().output.file_system
    if not fs_config:
        return
    timestamp = moment.timestamp()
    path = f'{fs_config.path}/{prefix}/{timestamp}.json'
    with open(path, 'w') as of:
        of.write(data)


def _write_data_to_s3_if_configured(data: str, prefix: str, moment: datetime) -> None:
    """
    Write data to AWS S3, if S3 output is configured.
    """
    aws_config = get_collector_config().output.aws
    if not aws_config:
        return

    timestamp = moment.timestamp()
    datestamp = moment.strftime('%Y/%m/%d')
    object_name = f'{aws_config.s3_prefix}/{datestamp}/{prefix}/{timestamp}.json'
    file_obj = BytesIO(data.encode('utf-8'))
    s3_client = boto3.client(
        service_name='s3',
        region_name=aws_config.region,
        aws_access_key_id=aws_config.access_key_id,
        aws_secret_access_key=aws_config.secret_access_key)
    try:
        s3_client.upload_fileobj(file_obj, aws_config.bucket, object_name)
    except ClientError as e:
        print(f'Error uploading to s3: {e} ')
