"""
Copyright 2021 Objectiv B.V.
"""

import os
from typing import NamedTuple, Optional

# All settings that are controlled through environment variables are listed at the top here, for a
# complete overview.
# These settings should not be accessed by the constants here, but through the functions defined
# below (e.g. get_config_output())
from objectiv_backend.schema.event_schemas import EventSchema, get_event_schema, get_event_list_schema
from objectiv_backend.common.types import EventListSchema

LOAD_BASE_SCHEMA = os.environ.get('LOAD_BASE_SCHEMA', 'true') == 'true'
SCHEMA_EXTENSION_DIRECTORY = os.environ.get('SCHEMA_EXTENSION_DIRECTORY')

# when set to true, the collector will return detailed validation errors per event
SCHEMA_VALIDATION_ERROR_REPORTING = os.environ.get('SCHEMA_VALIDATION_ERROR_REPORTING', 'false') == 'true'

# Number of ms before an event is considered too old. set to 0 to disable
MAX_DELAYED_EVENTS_MILLIS = 1000 * 3600

# Whether to run in sync mode (default) or async-mode.
_ASYNC_MODE = os.environ.get('ASYNC_MODE', '') == 'true'

# ### Postgres values.
# We define some default values here. DO NOT put actual passwords in here
_OUTPUT_ENABLE_PG = os.environ.get('OUTPUT_ENABLE_PG', 'true') == 'true'
_PG_HOSTNAME = os.environ.get('POSTGRES_HOSTNAME', 'localhost')
_PG_PORT = os.environ.get('POSTGRES_PORT', '5432')
_PG_DATABASE_NAME = os.environ.get('POSTGRES_DB', 'objectiv')
_PG_USER = os.environ.get('POSTGRES_USER', 'objectiv')
_PG_PASSWORD = os.environ.get('POSTGRES_PASSWORD', '')

# ### AWS S3 values, for writing data to S3.
# default access keys to an empty string, otherwise the boto library will default ot user defaults.
_OUTPUT_ENABLE_AWS = os.environ.get('OUTPUT_ENABLE_AWS', '') == 'true'
_AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID', '')
_AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY', '')
_AWS_REGION = os.environ.get('AWS_REGION', 'eu-west-1')
_AWS_BUCKET = os.environ.get('AWS_BUCKET', '')
_AWS_S3_PREFIX = os.environ.get('AWS_S3_PREFIX', '')

# ### Setting for outputting data to the filesystem
_OUTPUT_ENABLE_FILESYSTEM = os.environ.get('OUTPUT_ENABLE_FILESYSTEM', '') == 'true'
_FILESYSTEM_OUTPUT_DIR = os.environ.get('FILESYSTEM_OUTPUT_DIR')

# ### Snowplow settings
_SP_SCHEMA_COLLECTOR_PAYLOAD = 'iglu:com.snowplowanalytics.snowplow/CollectorPayload/thrift/1-0-0'
_SP_SCHEMA_CONTEXTS = 'iglu:com.snowplowanalytics.snowplow/contexts/jsonschema/1-0-0'
_SP_SCHEMA_OBJECTIV_TAXONOMY = 'iglu:io.objectiv/taxonomy/jsonschema/1-0-0'
_SP_SCHEMA_PAYLOAD_DATA = 'iglu:com.snowplowanalytics.snowplow/payload_data/jsonschema/1-0-4'
_SP_SCHEMA_SCHEMA_VIOLATIONS = 'iglu:com.snowplowanalytics.snowplow.badrows/schema_violations/jsonschema/2-0-0'

_SP_GCP_PROJECT = os.environ.get('SP_GCP_PROJECT', '')
_SP_GCP_PUBSUB_TOPIC_RAW = os.environ.get('SP_GCP_PUBSUB_TOPIC_RAW', '')
_SP_GCP_PUBSUB_TOPIC_BAD = os.environ.get('SP_GCP_PUBSUB_TOPIC_BAD', '')

_SP_AWS_MESSAGE_TOPIC_RAW = os.environ.get('SP_AWS_MESSAGE_TOPIC_RAW', '')
_SP_AWS_MESSAGE_TOPIC_BAD = os.environ.get('SP_AWS_MESSAGE_TOPIC_BAD', '')

# Cookie settings
_OBJ_COOKIE = 'obj_user_id'
# default cookie duration is 1 year, can be overridden by setting `COOKIE_DURATION`
_OBJ_COOKIE_DURATION = int(os.environ.get('COOKIE_DURATION', 60 * 60 * 24 * 365 * 1))

# Maximum number of events that a worker will process in a single batch. Only relevant in async mode
WORKER_BATCH_SIZE = 200
# Time to sleep, if there is no work to do for the workers. Only relevant in async mode
WORKER_SLEEP_SECONDS = 5


class AwsOutputConfig(NamedTuple):
    access_key_id: str
    secret_access_key: str
    region: str
    bucket: str
    s3_prefix: str


class FileSystemOutputConfig(NamedTuple):
    path: str


class PostgresConfig(NamedTuple):
    hostname: str
    port: int
    database_name: str
    user: str
    password: str


class SnowplowConfig(NamedTuple):
    gcp_enabled: bool
    gcp_project: str
    gcp_pubsub_topic_raw: str
    gcp_pubsub_topic_bad: str

    aws_enabled: bool
    aws_message_topic_raw: str
    aws_message_topic_bad: str
    aws_message_raw_type: str

    schema_collector_payload: str
    schema_contexts: str
    schema_objectiv_taxonomy: str
    schema_payload_data: str
    schema_schema_violations: str


class OutputConfig(NamedTuple):
    postgres: Optional[PostgresConfig]
    aws: Optional[AwsOutputConfig]
    file_system: Optional[FileSystemOutputConfig]
    snowplow: SnowplowConfig


class CookieConfig(NamedTuple):
    name: str
    # duration in seconds
    duration: int


class TimestampValidationConfig(NamedTuple):
    max_delay: int


class CollectorConfig(NamedTuple):
    async_mode: bool
    cookie: Optional[CookieConfig]
    error_reporting: bool
    output: OutputConfig
    event_schema: EventSchema
    event_list_schema: EventListSchema


def get_config_output_aws() -> Optional[AwsOutputConfig]:
    if not _OUTPUT_ENABLE_AWS:
        return None
    if _AWS_REGION and _AWS_ACCESS_KEY_ID and _AWS_SECRET_ACCESS_KEY and _AWS_BUCKET and _AWS_S3_PREFIX:
        raise ValueError(f'OUTPUT_ENABLE_AWS = true, but not all required values specified. '
                         f'Must specify AWS_REGION, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_BUCKET, '
                         f'and AWS_S3_PREFIX')
    return AwsOutputConfig(
        access_key_id=_AWS_ACCESS_KEY_ID,
        secret_access_key=_AWS_SECRET_ACCESS_KEY,
        region=_AWS_REGION,
        bucket=_AWS_BUCKET,
        s3_prefix=_AWS_S3_PREFIX
    )


def get_config_output_file_system() -> Optional[FileSystemOutputConfig]:
    if not _OUTPUT_ENABLE_FILESYSTEM:
        return None
    if not _FILESYSTEM_OUTPUT_DIR:
        raise ValueError('OUTPUT_ENABLE_FILESYSTEM = true, but FILESYSTEM_OUTPUT_DIR not specified.')
    return FileSystemOutputConfig(path=_FILESYSTEM_OUTPUT_DIR)


def get_config_postgres() -> Optional[PostgresConfig]:
    if not _OUTPUT_ENABLE_PG:
        return None
    if not _PG_HOSTNAME or not _PG_PORT or not _PG_DATABASE_NAME or not _PG_USER:
        raise ValueError(f'OUTPUT_ENABLE_PG = true, but not all required values specified. '
                         f'Must specify PG_HOSTNAME, PG_PORT, PG_DATABASE_NAME, PG_USER, and PG_PASSWORD')
    return PostgresConfig(
        hostname=_PG_HOSTNAME,
        port=int(_PG_PORT),
        database_name=_PG_DATABASE_NAME,
        user=_PG_USER,
        password=_PG_PASSWORD
    )


def get_config_output_snowplow() -> SnowplowConfig:
    if _SP_AWS_MESSAGE_TOPIC_RAW.startswith('https://sqs.'):
        aws_message_raw_type = 'sqs'
    else:
        aws_message_raw_type = 'kinesis'

    config = SnowplowConfig(
        gcp_enabled=(_SP_GCP_PROJECT != ''),
        gcp_project=_SP_GCP_PROJECT,
        gcp_pubsub_topic_raw=_SP_GCP_PUBSUB_TOPIC_RAW,
        gcp_pubsub_topic_bad=_SP_GCP_PUBSUB_TOPIC_BAD,

        aws_enabled=(_SP_AWS_MESSAGE_TOPIC_RAW != ''),
        aws_message_topic_raw=_SP_AWS_MESSAGE_TOPIC_RAW,
        aws_message_topic_bad=_SP_AWS_MESSAGE_TOPIC_BAD,
        aws_message_raw_type=aws_message_raw_type,

        schema_collector_payload=_SP_SCHEMA_COLLECTOR_PAYLOAD,
        schema_contexts=_SP_SCHEMA_CONTEXTS,
        schema_objectiv_taxonomy=_SP_SCHEMA_OBJECTIV_TAXONOMY,
        schema_payload_data=_SP_SCHEMA_PAYLOAD_DATA,
        schema_schema_violations=_SP_SCHEMA_SCHEMA_VIOLATIONS
    )
    if config.gcp_enabled:
        print(f'Enabled snowplow: GCP pipeline (raw:{config.gcp_pubsub_topic_raw} '
              f'/ bad:{config.gcp_pubsub_topic_bad})')

    if config.aws_enabled:
        print(f'Enabled Snowplow: AWS pipeline (raw({config.aws_message_raw_type}):{config.aws_message_topic_raw} '
              f'/ bad:{config.aws_message_topic_bad})')

    return config


def get_config_output() -> OutputConfig:
    """ Get the Collector's output settings. Raises an error if none of the outputs are configured. """
    output_config = OutputConfig(
        postgres=get_config_postgres(),
        aws=get_config_output_aws(),
        file_system=get_config_output_file_system(),
        snowplow=get_config_output_snowplow()
    )
    if not output_config.postgres \
            and not output_config.aws \
            and not output_config.file_system \
            and not output_config.snowplow:
        raise Exception('No output configured. At least configure either Postgres, S3 or FileSystem '
                        'output.')
    return output_config


def get_config_cookie() -> CookieConfig:
    return CookieConfig(
        name=_OBJ_COOKIE,
        duration=_OBJ_COOKIE_DURATION
    )


def get_config_event_schema() -> EventSchema:
    return get_event_schema(SCHEMA_EXTENSION_DIRECTORY)


def get_config_event_list_schema() -> EventListSchema:
    return get_event_list_schema()


def get_config_timestamp_validation() -> TimestampValidationConfig:
    return TimestampValidationConfig(max_delay=MAX_DELAYED_EVENTS_MILLIS)


# creating these configuration structures is not heavy, but it's pointless to do it for each request.
# so we have some super simple caching here
_CACHED_COLLECTOR_CONFIG: Optional[CollectorConfig] = None


def init_collector_config():
    """ Load collector config into cache. """
    global _CACHED_COLLECTOR_CONFIG
    _CACHED_COLLECTOR_CONFIG = CollectorConfig(
        async_mode=_ASYNC_MODE,
        cookie=get_config_cookie(),
        error_reporting=SCHEMA_VALIDATION_ERROR_REPORTING,
        output=get_config_output(),
        event_schema=get_config_event_schema(),
        event_list_schema=get_config_event_list_schema()
    )


def get_collector_config() -> CollectorConfig:
    """ Get the Collector Configuration from cache, or if not cached load it first. """
    global _CACHED_COLLECTOR_CONFIG
    if not _CACHED_COLLECTOR_CONFIG:
        init_collector_config()
        assert _CACHED_COLLECTOR_CONFIG is not None  # help out mypy
    return _CACHED_COLLECTOR_CONFIG
