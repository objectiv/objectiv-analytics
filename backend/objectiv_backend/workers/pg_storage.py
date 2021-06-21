"""
Copyright 2021 Objectiv B.V.
"""
import json
from datetime import datetime, timedelta
from typing import List

from psycopg2.extras import execute_values

from objectiv_backend.common.event_utils import get_context
from objectiv_backend.common.types import EventWithId, FailureReason


def insert_events_into_data(connection, events: List[EventWithId]):
    """
    Insert events into the 'data' table.

    This also tackles the problem of duplicate events. Postgres has a unique index on the event_id, so will
    not allow for two events with the same id to be inserted (a unique event). Here we check which events
    were not inserted (because they violated the uniqueness constraint), and those are inserted in the
    not-ok data table (nok_data).

    Does not do any transaction management, this merely issues insert commands. The insert might block if
    another transaction inserts events with the same event_ids. In extreme cases this function might even
    fail if the blocking exceeds the lock_timeout. To minimize impact of blocks and rollbacks, try to keep
    transactions that use this function short and do not insert too much data in one call

    This function assumes that the postgres connection has the isolation level
    ISOLATION_LEVEL_READ_COMMITTED set and a lock_timeout is configured.

    :param connection: psycopg2 database connection, must have ISOLATION_LEVEL_READ_COMMITTED set.
    :param events: list of events. Each event must be a valid Event, and must have a CookieIdContext
    :raise Exception: If the database is not available, or if it blocks longer than lock_timeout.
    """
    if not events:
        return

    # We use 'on conflict do nothing'. With the read-committed isolation level this guarantees that this
    # transaction will not insert a row that will conflict with another transaction, even if the results
    # of that transaction are not yet visible to this transaction [1]. This guarantees that the transaction
    # will not fail later on at commit time, because there will be no conflicting rows at that time.
    # Furthermore the returning clause is guaranteed to only return the actually inserted rows [2]. So we
    # can use that to determine which rows were skipped because they violated the uniqueness constraint.
    #
    # An disadvantage of this is that the insert might block if another transaction is inserting an event
    # with the same event_id. Postgres won't know whether the rows are conflicting until the potentially
    # conflicting transaction commits, and therefore has no choice but to block. If the block exceeds the
    # lock_timeout then this will result in a failed transaction, and this function will raise an
    # exception.
    #
    # [1] https://www.postgresql.org/docs/13/transaction-iso.html
    # [2] https://www.postgresql.org/docs/13/sql-insert.html
    insert_query = f'''
        insert into data(event_id, day, moment, cookie_id, value)
        values %s
        on conflict(event_id) do nothing
        returning event_id
    '''
    values = []
    for event in events:
        timestamp = _millis_to_datetime(event.event['time'])
        cookie_id = get_context(event.event, 'CookieIdContext')['cookie_id']
        value = (str(event.id),
                 timestamp,
                 timestamp,
                 cookie_id,
                 json.dumps(event.event))
        values.append(value)
    with connection.cursor() as cursor:
        inserted_event_ids = execute_values(
            cursor, insert_query, values, template=None, page_size=100, fetch=True)

    # Determine whether there were any duplicate events that were already in the table
    # In case of duplicate events, we'll add those to the nok_data table for traceability
    duplicate_events = []
    if len(inserted_event_ids) < len(events):
        inserted_event_ids_set = set(inserted_event_ids)
        for event in events:
            if event.id not in inserted_event_ids_set:
                duplicate_events.append(event)
    if duplicate_events:
        print(f'Duplicate events found, count: {len(duplicate_events)}. '
              f'Will be inserted in nok_data table.')
        insert_events_into_nok_data(connection, duplicate_events, reason=FailureReason.DUPLICATE)


def insert_events_into_nok_data(connection,
                                events: List[EventWithId],
                                reason: FailureReason = FailureReason.FAILED_VALIDATION):
    """
    Insert events into the not-ok data ('nok_data') table
    Does not do any transaction management, this merely issues insert commands.
    :param connection: db connection
    :param events: list of events. Each event must have a CookieIdContext
    :param reason: Why are these events written to the nok_data table.
    """
    if not events:
        return

    insert_query = f'insert into nok_data (event_id, day, moment, cookie_id, value, reason) values %s'
    values = []
    for event in events:
        timestamp = _millis_to_datetime(event.event['time'])
        cookie_id = get_context(event.event, 'CookieIdContext')['cookie_id']
        value = (str(event.id),
                 timestamp,
                 timestamp,
                 cookie_id,
                 json.dumps(event.event),
                 reason.value)
        values.append(value)
    with connection.cursor() as cursor:
        execute_values(cursor, insert_query, values, template=None, page_size=100)


def _millis_to_datetime(millis: int) -> datetime:
    """
    Convert an int with milliseconds since the epoch to a datetime object with milliseconds accuracy.
    """
    _event_seconds = millis // 1000
    _milli_seconds = millis % 1000
    timestamp = datetime.utcfromtimestamp(_event_seconds) + timedelta(milliseconds=_milli_seconds)
    return timestamp
