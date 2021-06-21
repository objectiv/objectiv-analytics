"""
Copyright 2021 Objectiv B.V.
"""

import os
from typing import NamedTuple, Optional

# All settings that are controlled through environment variables are listed at the top here, for a
# complete overview.
# These settings should not be accessed by the constants here, but through the functions defined
# below (e.g. get_config_output())
from objectiv_backend.schema.event_schemas import EventSchema, get_event_schema

SCHEMA_EXTENSION_DIRECTORY = os.environ.get('SCHEMA_EXTENSION_DIRECTORY')

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

# Cookie settings
_OBJ_COOKIE = 'obj_user_id'
_OBJ_COOKIE_DURATION = 60 * 60 * 24 * 365 * 5

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


class OutputConfig(NamedTuple):
    postgres: Optional[PostgresConfig]
    aws: Optional[AwsOutputConfig]
    file_system: Optional[FileSystemOutputConfig]


class CookieConfig(NamedTuple):
    name: str
    # duration in seconds
    duration: int


class CollectorConfig(NamedTuple):
    async_mode: bool
    cookie: Optional[CookieConfig]
    output: OutputConfig
    schema: EventSchema


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


def get_config_output() -> OutputConfig:
    """ Get the Collector's output settings. Raises an error if none of the outputs are configured. """
    output_config = OutputConfig(
        postgres=get_config_postgres(),
        aws=get_config_output_aws(),
        file_system=get_config_output_file_system()
    )
    if not output_config.postgres and not output_config.aws and not output_config.file_system:
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


# creating these configuration structures is not heavy, but it's pointless to do it for each request.
# so we have some super simple caching here
_CACHED_COLLECTOR_CONFIG: Optional[CollectorConfig] = None


def init_collector_config():
    """ Load collector config into cache. """
    global _CACHED_COLLECTOR_CONFIG
    _CACHED_COLLECTOR_CONFIG = CollectorConfig(
        async_mode=_ASYNC_MODE,
        cookie=get_config_cookie(),
        output=get_config_output(),
        schema=get_config_event_schema()
    )


def get_collector_config() -> CollectorConfig:
    """ Get the Collector Configuration from cache, or if not cached load it first. """
    global _CACHED_COLLECTOR_CONFIG
    if not _CACHED_COLLECTOR_CONFIG:
        init_collector_config()
        assert _CACHED_COLLECTOR_CONFIG is not None  # help out mypy
    return _CACHED_COLLECTOR_CONFIG
