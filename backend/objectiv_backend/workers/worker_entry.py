"""
Copyright 2021 Objectiv B.V.
"""
import sys
from typing import List, Tuple

from objectiv_backend.common.config import WORKER_BATCH_SIZE, get_config_event_schema
from objectiv_backend.common.types import EventWithId
from objectiv_backend.schema.hydrate_events import hydrate_types_into_event
from objectiv_backend.schema.validate_events import validate_event_adheres_to_schema
from objectiv_backend.workers.pg_queues import PostgresQueues, ProcessingStage
from objectiv_backend.workers.pg_storage import insert_events_into_nok_data
from objectiv_backend.workers.util import worker_main


def main_entry(connection) -> int:
    """
    Pick events from the entry queue and insert them into the finalize queue.
    :return number of processed events
    """
    with connection:
        pg_queues = PostgresQueues(connection=connection)
        events: List[EventWithId] = pg_queues.get_events(queue=ProcessingStage.ENTRY,
                                                         max_items=WORKER_BATCH_SIZE)
        print(f'event-ids: {sorted(event.id for event in events)}')

        ok_events, nok_events = process_events_entry(events)
        # ok_events continue on the happy path
        # nok_events failed to validate and are written to the nok_data table
        pg_queues.put_events(queue=ProcessingStage.FINALIZE, events=ok_events)
        insert_events_into_nok_data(connection=connection, events=nok_events)
    return len(events)


def process_events_entry(events: List[EventWithId]) -> Tuple[List[EventWithId], List[EventWithId]]:
    """
    Two step processing of events:
    1) Modify events: hydrate all parent types of both the event and contexts into the event
    2) Split event list on events that pass validation and those that don't

    :param events: List of events. validate_structure_event_list() must pass on this list.
    :return: tuple with two lists. Both lists have the hydrated types.
        1) ok events: events that passed validation
        2) not-ok events: events that didn't pass validation
    """
    ok_events = []
    nok_events = []
    event_schema = get_config_event_schema()
    for event_w_id in events:
        event = event_w_id.event

        error_info = validate_event_adheres_to_schema(event_schema=event_schema, event=event)
        if error_info:
            print(f'error, event_id: {event_w_id.id}, errors: {[ei.info for ei in error_info]}')
            nok_events.append(event_w_id)
        else:
            event = hydrate_types_into_event(event_schema=event_schema, event=event)
            event_w_id = EventWithId(id=event_w_id.id, event=event)
            ok_events.append(event_w_id)
    return ok_events, nok_events


if __name__ == '__main__':
    _loop = sys.argv[1:2] == ['--loop']
    worker_main(function=main_entry, loop=_loop)
