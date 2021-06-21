"""
Copyright 2021 Objectiv B.V.
"""
import psycopg2
from psycopg2 import extras
from psycopg2.extensions import ISOLATION_LEVEL_READ_COMMITTED

from objectiv_backend.common.config import PostgresConfig


def get_db_connection(pg_config: PostgresConfig):
    """
    Give a psycopg2 connection with:
     * read committed isolation level
     * 5 second lock_timeout
     * uuids enabled.
    """
    conn = psycopg2.connect(user=pg_config.user,
                            password=pg_config.password,
                            host=pg_config.hostname,
                            port=pg_config.port,
                            database=pg_config.database_name)
    # The code in pg_storage.py and pg_queues.py assumes the read_committed isolation level
    # Additionally, the function insert_events_into_data() might block if another transaction tries to
    # insert the same event_id and that other transaction. We set lock-timeout to guarantee unblocking,
    # even if somehow another conflicting transaction doesn't progress anymore.
    conn.set_session(isolation_level=ISOLATION_LEVEL_READ_COMMITTED)
    # Five seconds seems like a reasonable value for lock_timeout. If a blocking transaction takes more
    # than 5 seconds, something is wrong.
    with conn.cursor() as cursor:
        cursor.execute("set lock_timeout='5s';")
    extras.register_uuid()
    return conn
