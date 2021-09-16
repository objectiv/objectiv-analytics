"""
Copyright 2021 Objectiv B.V.
"""
import argparse
import json
import sys
from typing import List

from objectiv_backend.schema.event_schemas import EventSchema, get_event_schema
from objectiv_backend.schema.validate_events import validate_event_list
from objectiv_backend.common.types import EventData


def hydrate_types_into_event(event_schema: EventSchema, event: EventData) -> EventData:
    """
    Modifies the given event:
        1. adds a "events" field: a list of all inherited event-types (including the event)
        2. For each context adds a "_types" fields: a list of all inherited context-types
    :param event_schema: schema to use for type-hydration
    :param event: event object. Must have passed event validation by validate_events.validate_event_data.
    :return: The modified event object.
    """
    event_name = event['_type']
    all_event_types = event_schema.get_all_parent_event_types(event_name)
    event["_types"] = sorted(all_event_types)
    global_contexts = event['global_contexts']
    for context in global_contexts:
        context["_types"] = sorted(
            event_schema.get_all_parent_context_types(context["_type"])
        )
    location_stack = event['location_stack']
    for context in location_stack:
        context["_types"] = sorted(
            event_schema.get_all_parent_context_types(context["_type"])
        )
    return event


def main(argv: List[str]):
    parser = argparse.ArgumentParser(description='Hydrate events')
    parser.add_argument('--schema-extensions-directory', type=str)
    parser.add_argument('filenames', type=str, nargs='+')
    args = parser.parse_args(argv[1:])

    filenames = args.filenames
    event_schema = get_event_schema(schema_extensions_directory=args.schema_extensions_directory)

    for filename in filenames:
        with open(filename) as file:
            event_data = json.loads(file.read())
        errors = validate_event_list(event_schema=event_schema, event_data=event_data['events'])
        if errors:
            raise Exception(f'Error in file: {filename} - {errors}')
        events = event_data['events']
        print(
            json.dumps(
                [hydrate_types_into_event(event_schema, event) for event in events],
                indent=4
            )
        )


if __name__ == '__main__':
    main(sys.argv)
