"""
Copyright 2021 Objectiv B.V.

Functions to write data to S3 and the local filesystem.

This is experimental code, and not ready for production use.
"""
import json
from datetime import datetime
from io import BytesIO

from typing import List


from objectiv_backend.common.config import get_collector_config, SnowplowConfig
from objectiv_backend.common.types import EventDataList
from objectiv_backend.schema.validate_events import EventError
from objectiv_backend.snowplow.snowplow_helper import write_data_to_aws_pipeline, write_data_to_gcp_pubsub

if get_collector_config().output.aws:
    import boto3
    from botocore.exceptions import ClientError


def events_to_json(events: EventDataList) -> str:
    """
    Convert list of events to a string with on each line a json object representing a single event.
    Note that the returned string is not a json list; This format makes it suitable as raw input to AWS
    Athena.
    """
    return json.dumps(events)


def write_data_to_fs_if_configured(data: str, prefix: str, moment: datetime) -> None:
    """
    Write data to disk, if file_system output is configured. If file_system output is not configured, then
    this function returns directly.
    :param data: data to write
    :param prefix: directory prefix, added to path after the configured path/ and before /filename.json
    :param moment: timestamp that the data arrived
    """
    fs_config = get_collector_config().output.file_system
    if not fs_config:
        return
    timestamp = moment.timestamp()
    path = f'{fs_config.path}/{prefix}/{timestamp}.json'
    with open(path, 'w') as of:
        of.write(data)


def write_data_to_s3_if_configured(data: str, prefix: str, moment: datetime) -> None:
    """
    Write data to AWS S3, if S3 output is configured. if aws s3 output is not configured, then this
    function returns directly.
    :param data: data to write
    :param prefix: prefix, included in the keyname after the configured path/ and datestamp/ and
        before /filename.json
    :param moment: timestamp that the data arrived
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


def write_data_to_snowplow_if_configured(events: EventDataList,
                                         good: bool,
                                         event_errors: List[EventError] = None) -> None:
    """
    Write data to Snowplow pipeline if either GCP or AWS for Snowplow if configures
    :param events: EventDataList
    :param prefix: should be either OK or NOK
    :param event_errors: list of errors, if any
    :return:
    """
    config: SnowplowConfig = get_collector_config().output.snowplow

    if config.aws_enabled:
        write_data_to_aws_pipeline(events=events, config=config, good=good, event_errors=event_errors)

    if config.gcp_enabled:
        write_data_to_gcp_pubsub(events=events, config=config, good=good, event_errors=event_errors)
