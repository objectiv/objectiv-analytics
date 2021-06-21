"""
Copyright 2021 Objectiv B.V.
"""
import json
import uuid
from enum import Enum
from typing import List, Tuple

import psycopg2
from psycopg2.extras import execute_values

from objectiv_backend.common.types import EventWithId


class ProcessingStage(Enum):
    ENTRY = "entry"
    FINALIZE = "finalize"


class PostgresQueues:
    """
    Class to interact with the event queues in Postgres.

    Does not do any transaction management, i.e. does not start, commit or rollback transactions.
    Calling code must make sure to start and commit transactions. If needed transactions can be rolled
    back by the calling code, which will undo the actions of get_events and put_events.

    This class assumes that the postgres connection has the isolation level ISOLATION_LEVEL_READ_COMMITTED
    set.
    """

    def __init__(self, connection):
        """
        Create a new PostgresQueues object
        :param connection: psycopg2 database connection, must have ISOLATION_LEVEL_READ_COMMITTED set.
        """
        self.connection = connection

    @staticmethod
    def _queue_to_table(queue: ProcessingStage):
        if queue == ProcessingStage.ENTRY:
            return 'queue_entry'
        if queue == ProcessingStage.FINALIZE:
            return 'queue_finalize'
        raise Exception('Implementation incomplete')

    def get_events(self, queue: ProcessingStage, max_items: int) -> List[EventWithId]:
        """
        Get a list of events from a queue for processing.

        :param queue: Queue from which to pick events
        :param max_items: maximum number of items to pick from the queue.
        :return: list of events with id, at most max_items, but can be less.
        """
        table_name = self._queue_to_table(queue)
        query = f'''
            delete from {table_name}
            where event_id in (
                select event_id
                from {table_name}
                order by insert_order asc
                limit %s
                for update skip locked
            )
            returning event_id, value;
        '''
        with self.connection.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor) as cursor:
            cursor.execute(query, (max_items, ))
            events_with_id = [EventWithId(id=row.event_id, event=row.value) for row in cursor.fetchall()]
        return events_with_id

    def put_events(self,
                   queue: ProcessingStage,
                   events: List[EventWithId]):
        """
        Put an event with a given event-id on a queue

        :param queue: Which queue to put the event on
        :param events: list of events with ids
        """
        if not events:
            return
        table_name = self._queue_to_table(queue)
        insert_query = f'''
            insert into
            {table_name}(event_id, value)
            values %s
            '''
        values: List[Tuple[uuid.UUID, str]] = [(event.id, json.dumps(event.event)) for event in events]
        with self.connection.cursor() as cursor:
            execute_values(cursor, insert_query, values, template=None, page_size=100)
