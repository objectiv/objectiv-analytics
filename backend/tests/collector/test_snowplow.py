import json
import jsonschema
import base64
from objectiv_backend.snowplow.schema.ttypes import CollectorPayload
from objectiv_backend.snowplow.snowplow_helper import make_snowplow_custom_context, \
    objectiv_event_to_snowplow, objectiv_event_to_snowplow_payload, snowplow_schema_violation_json
from tests.schema.test_schema import CLICK_EVENT_JSON, make_event_from_dict
from objectiv_backend.common.config import SnowplowConfig
from objectiv_backend.schema.validate_events import EventError, ErrorInfo


config = SnowplowConfig(
    schema_contexts='test-schema-contexts',
    schema_payload_data='test-schema-payload-data',
    schema_objectiv_taxonomy='test-schema-objectiv-taxonomy',
    schema_collector_payload='',
    schema_schema_violations='https://raw.githubusercontent.com/snowplow/iglu-central/master/schemas/com.snowplowanalytics.snowplow.badrows/schema_violations/jsonschema/2-0-0',

    gcp_enabled=False,
    gcp_project='',
    gcp_pubsub_topic_raw='',
    gcp_pubsub_topic_bad='',

    aws_enabled=False,
    aws_message_topic_raw='',
    aws_message_topic_bad='',
    aws_message_raw_type=''
)

event_list = json.loads(CLICK_EVENT_JSON)
event = make_event_from_dict(event_list['events'][0])


def test_objectiv_event_to_snowplow():

    sp_event = objectiv_event_to_snowplow(event=event, config=config)
    assert type(sp_event) == dict

    assert sp_event['schema'] == config.schema_objectiv_taxonomy
    assert sp_event['data'] == event


def test_make_snowplow_custom_context():
    sp_event = objectiv_event_to_snowplow(event=event, config=config)
    encoded_context = make_snowplow_custom_context(self_describing_event=sp_event, config=config)

    json_context = base64.b64decode(encoded_context)
    context = json.loads(json_context)

    # check that this is in fact a context conforming to the contexts schema we set
    assert context['schema'] == config.schema_contexts

    assert context['data'][0]
    context_data = context['data'][0]
    # check we can find the original objectiv event inside of it
    assert context_data['schema'] == config.schema_objectiv_taxonomy

    # check to see the data is still the same as the original event
    assert context_data['data'] == event


def test_objectiv_event_to_snowplow_payload():

    collector_payload = objectiv_event_to_snowplow_payload(event=event, config=config)
    # check iof we get ther proper object
    assert type(collector_payload) == CollectorPayload

    # check if the schema is correct
    assert collector_payload.schema == config.schema_collector_payload

    body = json.loads(collector_payload.body)
    # check the schema of the body attribute
    assert body['schema'] == config.schema_payload_data

    # check if we can deserialize the encoded custom context properly
    assert json.loads(base64.b64decode(body['data'][0]['cx']))


def test_snowplow_failed_event():
    # as we do no actual validation of the event, there's no need to use an invalid event.
    event_error = EventError(
        event_id=event['id'],
        error_info=[
            ErrorInfo(
                data=[],
                info='test')
        ])

    payload = objectiv_event_to_snowplow_payload(event=event, config=config)
    violation = snowplow_schema_violation_json(payload=payload, config=config, event_error=event_error)

    # local copy of https://raw.githubusercontent.com/snowplow/iglu-central/master/schemas/com.snowplowanalytics.snowplow.badrows/schema_violations/jsonschema/2-0-0
    with open('tests/collector/schema_violations.json') as fp:
        schema = json.load(fp)

        # somehow doesn't like the self-describing schema schema from Snowplow
        # so remove it, so we fall back to a generic schema (which is used to validate the schema, not the event)
        del schema['$schema']
        instance = violation['data']

        jsonschema.validate(instance=instance, schema=schema,)
