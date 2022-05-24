from typing import Dict, List, Union

import base64
import json
from datetime import datetime
from urllib.parse import urlparse

from objectiv_backend.snowplow.schema.ttypes import CollectorPayload  # type: ignore

from objectiv_backend.common.config import SnowplowConfig, get_collector_config
from objectiv_backend.common.event_utils import get_context
from objectiv_backend.common.types import EventDataList, EventData
from objectiv_backend.schema.validate_events import EventError

from thrift.protocol import TBinaryProtocol
from thrift.transport import TTransport

# only load imports if needed
snowplow_config = get_collector_config().output.snowplow
if snowplow_config.gcp_enabled:
    from google.cloud import pubsub_v1
    from google.api_core.exceptions import NotFound

if snowplow_config.aws_enabled:
    import boto3
    import botocore.exceptions


def make_snowplow_custom_context(self_describing_event: Dict, config: SnowplowConfig) -> str:
    """
    Create Snowplow custom context, containing snowplow_event, base64 encoded, ready to be inserted into a
    snowplow event
    :param self_describing_event: Dict containing a schema and a payload
    :param config: SnowplowConfig
    :return: base64 encoded snowplow self-describing custom context
    """
    snowplow_contexts_schema = config.schema_contexts
    custom_context = {
        'schema': snowplow_contexts_schema,
        'data': [self_describing_event]
    }
    custom_context_json = json.dumps(custom_context)
    return str(base64.b64encode(custom_context_json.encode('UTF-8')), 'UTF-8')


def objectiv_event_to_snowplow(event: EventData, config: SnowplowConfig) -> Dict[str, Union[str, EventData]]:
    """
    Wrap objectiv event in self-describing Snowplow object
    :param event: EventData
    :param config: SnowplowConfig
    :return: Dict containing event and schema describing the event
    """
    objectiv_schema = config.schema_objectiv_taxonomy

    return {
        'schema': objectiv_schema,
        'data': event
    }


def objectiv_event_to_snowplow_payload(event: EventData, config: SnowplowConfig) -> CollectorPayload:
    """
    Transform Objectiv event to Snowplow Collector Payload object
    :param event: EventData
    :param config: SnowplowConfig
    :return: CollectorPayload
    """
    snowplow_payload_data_schema = config.schema_payload_data
    snowplow_collector_payload_schema = config.schema_collector_payload

    try:
        http_context = get_context(event, 'HttpContext')
    except ValueError:
        http_context = {}

    try:
        cookie_context = get_context(event, 'CookieIdContext')
    except ValueError:
        cookie_context = {}

    try:
        path_context = get_context(event, 'PathContext')
    except ValueError:
        path_context = {}

    query_string = urlparse(str(path_context.get('id', ''))).query

    rich_event = {'event_id' if k == 'id' else k: v for k, v in event.items()}
    rich_event['cookie_id'] = cookie_context.get('id', '')

    snowplow_event = objectiv_event_to_snowplow(event=rich_event, config=config)
    snowplow_custom_context = make_snowplow_custom_context(self_describing_event=snowplow_event, config=config)
    payload = {
        "schema": snowplow_payload_data_schema,
        "data": [{
            "e": "se",  # mandatory: event type: structured event
            "p": "web",  # mandatory: platform
            "tv": "objectiv-tracker-0.0.5",  # mandatory: tracker version
            "eid": event['id'],  # event_id
            "url": path_context.get('id', ''),
            "cx": snowplow_custom_context
        }]
    }
    return CollectorPayload(
        schema=snowplow_collector_payload_schema,
        ipAddress=http_context.get('remote_address', ''),
        timestamp=int(datetime.now().timestamp() * 1000),
        encoding='UTF-8',
        collector='objectiv_collector',
        userAgent=http_context.get('user_agent', ''),
        refererUri=http_context.get('referrer', ''),
        path='/com.snowplowanalytics.snowplow/tp2',
        querystring=query_string,
        body=json.dumps(payload),
        headers=[],
        contentType='application/json',
        hostname='',
        networkUserId=cookie_context.get('id', '')
    )


def payload_to_thrift(payload: CollectorPayload) -> bytes:
    """
    Generate Thrift message for payload, based on Thrift schema here:
        https://github.com/snowplow/snowplow/blob/master/2-collectors/thrift-schemas/collector-payload-1/src/main/thrift/collector-payload.thrift
    :param payload: CollectorPayload - class instance representing Thrift message
    :return: bytes - serialized string
    """

    # use memory buffer as transport layer
    trans = TTransport.TMemoryBuffer()

    # use the binary encoding protocol
    oprot = TBinaryProtocol.TBinaryProtocol(trans=trans)
    payload.write(oprot=oprot)

    return trans.getvalue()


def snowplow_schema_violation_json(payload: CollectorPayload, config: SnowplowConfig,
                                   event_error: EventError = None) -> Dict[str, Union[str, Dict]]:
    """
    Generate Snowplow schema violation JSON object
    :param payload: CollectorPayload object - representation of Event
    :param config: SnowplowConfig
    :param event_error: error for this event
    :return: Dictionary representing the schema violation
    """

    data_reports = []

    if event_error and event_error.error_info:
        for ei in event_error.error_info:
            data_reports.append({
                "message": ei.info,
                "path": '$',
                "keyword": "required",
                "targets": ["_type"]
            })

    parameters = []
    data = json.loads(payload.body)['data'][0]
    for key, value in data.items():
        parameters.append({
            "name": key,
            "value": value[:512]
        })

    # look for our custom context, so we can fill the enrich section
    event = {}
    if 'cx' in data:
        context_container_encoded = data['cx']
        context_container_decoded = json.loads(base64.b64decode(context_container_encoded).decode('utf-8'))
        contexts = context_container_decoded['data']
        for context in contexts:
            if 'schema' in context and context['schema'] == config.schema_objectiv_taxonomy and 'data' in context:
                event = context['data']
                # we pick the first
                break

    ts_format = '%Y-%m-%dT%H:%M:%S.%fZ'
    return {
        "schema": config.schema_schema_violations,
        # Information regarding the schema violations
        "data": {
            #   "required": [ "failure", "payload", "processor" ],
            "failure": {
                # Timestamp at which the failure occurred --> 2022-03-11T09:37:47.093932Z
                "timestamp": datetime.now().strftime(ts_format),
                # List of failure messages associated with the tracker protocol violations
                "messages": [
                    {
                    "schemaKey": config.schema_objectiv_taxonomy,
                    "error": {
                        "error": "ValidationError",
                        "dataReports": data_reports
                        }
                    }
                ]
            },
            #
            "payload": {
                # The raw event extracted from collector payload
                # "required": [ "vendor", "version", "loaderName", "encoding" ]
                "raw": {
                    # Vendor of the adapter that processed this payload, (com.snowplowanalytics.snowplow)
                    "vendor": 'io.objectiv',
                    # Version of the adapter that processed this payload (tp2)
                    "version": '1',

                    "loaderName": 'objectiv_collector',
                    # Encoding of the collector payload
                    "encoding": payload.encoding,
                    # Query string of the collector payload containing this event
                    "parameters": parameters,
                    # Content type of the payload as detected by the collector
                    "contentType": payload.contentType,
                    "headers": payload.headers,
                    "ipAddress": payload.ipAddress,
                    "refererUri": payload.refererUri,
                    "timestamp": datetime.fromtimestamp(payload.timestamp/1000).strftime(ts_format),
                    "useragent": payload.userAgent,
                    "userId": payload.networkUserId
                },
                "enrich": {
                    "event_id": event.get('id'),
                    "context": context_container_encoded
                }
            },
            # Information about the piece of software responsible for the creation of schema violations
            "processor": {
                # Artifact responsible for the creation of schema violations
                "artifact": 'objectiv-collector',
                # Version of the artifact responsible for the creation of schema violations
                "version": "0.0.1"
            }
        }
    }


def prepare_event_for_snowplow_pipeline(event: EventData,
                                        good: bool,
                                        config: SnowplowConfig,
                                        event_errors: List[EventError] = None) -> bytes:
    """
    Transform event into data suitable for writing to the Snowplow Pipeline. If the event is "good" this means a
    CollectorPayload object, binary-encoded using Thrift. If it's a bad event, it's transformed to a JSON-based schema
    violation.
    :param event: EventData
    :param good: bool - True if these events should go to the "good" channel
    :param config: SnowplowConfig
    :param event_errors: list of EventError
    :return: bytes object to be ingested by Snowplow pipeline
    """
    payload: CollectorPayload = objectiv_event_to_snowplow_payload(event=event, config=config)
    if good:
        data = payload_to_thrift(payload=payload)
    else:
        event_error = None
        # try to find errors for the current event_id
        if event_errors:
            for ee in event_errors:
                if ee.event_id == event['id']:
                    event_error = ee
        failed_event = snowplow_schema_violation_json(payload=payload, config=config, event_error=event_error)

        # serialize (json) and encode to bytestring for publishing
        data = json.dumps(failed_event, separators=(',', ':')).encode('utf-8')

    return data


def write_data_to_gcp_pubsub(events: EventDataList, config: SnowplowConfig, good: bool = True,
                             event_errors: List[EventError] = None) -> None:
    """
    Write provided list of events to the Snowplow GCP pipeline, using GCP PubSub
    :param events: EventDataList - List of EventData
    :param config:  SnowplowConfig
    :param good: bool - True if these events should go to the "good" channel
    :param event_errors: list of EventErrors
    :return:
    """

    project = config.gcp_project
    if good:
        # good events get sent to the raw topic, which means they get processed by snowplow's enrichment
        topic = config.gcp_pubsub_topic_raw
    else:
        # not ok events get sent to the bad topic
        topic = config.gcp_pubsub_topic_bad

    publisher = pubsub_v1.PublisherClient()
    topic_path = f'projects/{project}/topics/{topic}'

    for event in events:
        data = prepare_event_for_snowplow_pipeline(event=event, good=good, event_errors=event_errors, config=config)

        try:
            publisher.publish(topic_path, data=data)
        except NotFound as e:
            print(f'PubSub topic {topic} could not be found! {e}')


def write_data_to_aws_pipeline(events: EventDataList, config: SnowplowConfig,
                               good: bool = True,
                               event_errors: List[EventError] = None) -> None:
    """
    Write provided list of events to Snowplow AWS pipeline, either directly to Kinesis, or to SQS
    :param events: EventDataList - List of EventData
    :param config:  SnowplowConfig
    :param good: bool - True if these events should go to the "good" channel
    :param event_errors: list of EventErrors
    :return:
    """

    if good:
        # good events get sent to the raw topic, which means they get processed by snowplow's enrichment
        stream_name = config.aws_message_topic_raw

        # config determines whether we use sqs for raw events
        client_type = config.aws_message_raw_type
    else:
        stream_name = config.aws_message_topic_bad
        # the bad stream always goes to kinesis
        client_type = 'kinesis'

    if client_type == 'kinesis':
        client = boto3.client('kinesis')
    else:
        client = boto3.client('sqs')

    for event in events:
        data = prepare_event_for_snowplow_pipeline(event=event, good=good, event_errors=event_errors, config=config)

        if client_type == 'kinesis':
            try:
                client.put_record(
                    StreamName=stream_name,
                    Data=data,
                    PartitionKey='event_id')
            except client.exceptions.ProvisionedThroughputExceededException as e:
                print(f'Could not deliver event to Kinesis: throughput exceeded in {stream_name}: {e}')
            except botocore.exceptions.ClientError as e:
                print(f'Exception sending event to Kinesis ({stream_name}: {e}')

        elif client_type == 'sqs':
            # sqs doesn't support binary payloads, so in this case we base64 encode
            payload = str(base64.b64encode(data), 'UTF-8')

            try:
                client.send_message(QueueUrl=stream_name,
                                    MessageBody=payload,
                                    MessageAttributes={
                                        #  The sqs message attribute that will be used to set the kinesis partition key
                                        'kinesisKey': {
                                            'StringValue': 'event_id',
                                            'DataType': 'String'
                                        }
                                    })
            except client.exceptions.InvalidMessageContents as e:
                print(f'Failed to deliver event to SQS: Invalid Message Contents ({stream_name}: {e}')
            except botocore.exceptions.ClientError as e:
                print(f'Failed to deliver event to SQS ({stream_name}: {e}')

        else:
            # this should never happen
            raise ValueError(f'Unknown Client-Type: {client_type}')

