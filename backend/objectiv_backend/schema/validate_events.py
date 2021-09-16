"""
Copyright 2021 Objectiv B.V.
"""
import argparse
import json
import sys
from typing import List, Any, Dict, NamedTuple
import uuid
import re

import jsonschema
from jsonschema import ValidationError

from objectiv_backend.schema.event_schemas import EventSchema, get_event_schema
from objectiv_backend.common.config import \
    get_config_timestamp_validation, get_collector_config

from objectiv_backend.common.types import EventData


class ErrorInfo(NamedTuple):
    data: Any
    info: str

    def asdict(self):
        return self._asdict()


class EventError(Dict):
    event_id: uuid.UUID
    error_info: List[ErrorInfo]

    def __init__(self, event_id: uuid.UUID, error_info: List[ErrorInfo]):
        self.event_id = event_id
        self.error_info = error_info

        # we use a dictionary representation, to make sure we can serialize it with the JSON encoder
        dict.__init__(self, event_id=event_id.__str__(), error_info=[e.asdict() for e in error_info])


def get_event_list_schema() -> Dict[str, Any]:
    """

    :return: a dictionary containing a JSON schema like string to validate an array of events
    """
    event_schema = get_collector_config().event_schema
    events = event_schema.events.schema

    # we use AbstractEvent as the blueprint for what an event should look like
    abstract_event = events['AbstractEvent']

    # # list of properties for an event (can be nested)
    items: Dict[str, dict] = {}
    for property_name, property_desc in abstract_event['properties'].items():

        if 'items' in property_desc and re.match('^Abstract.*?Context$', property_desc['items']['type']):
            # we don't want to go into the validation / schema of contexts here
            # so a simple object will suffice
            property_desc['items']['type'] = 'object'
        items[property_name] = property_desc

    # we want a schema for a list of events (the base_schema only specifies a single event)
    # the schema wants a list of abstract events. As that is not a valid JSON type,
    # we replace that type with the more generic 'object' type, and the actual definition of
    # an abstract event
    event_list_schema = get_collector_config().event_list_schema
    if 'events' in event_list_schema['properties'] and \
            'items' in event_list_schema['properties']['events'] and \
            'type' in event_list_schema['properties']['events']['items'] and \
            event_list_schema['properties']['events']['items']['type'] == 'AbstractEvent':
        event_list_schema['properties']['events']['items'] = {
            'type': 'object',
            'items': items
        }
    return event_list_schema


def validate_structure_event_list(event_data: Any) -> List[ErrorInfo]:
    """
    Checks that event_data is a list of events, that each event has the required fields, and that all
        contexts have the base required fields (id and _type).
    Does not perform any schema-dependent validation, e.g. doesn't check that the event type is valid,
    that an event has the right contexts, or that contexts have the right fields. For those checks call
    validate_event_adheres_to_schema on each individual event.
    :return: list of found errors. Empty list indicates not errors
    """
    try:
        event_list_schema = get_event_list_schema()
        jsonschema.validate(instance=event_data, schema=event_list_schema)
    except ValidationError as exc:
        return [ErrorInfo(event_data, f'Overall structure does not adhere to schema: {exc}')]
    return []


def validate_event_list(event_schema: EventSchema, event_data: Any) -> List[ErrorInfo]:
    """
    Checks that the event data is correct.
    Checks done:
        - Overall structure is correct (using validate_structure_event_list())
        - All events in the list adhere to the EventSchema
    :param event_schema: schema to validate against
    :param event_data: list of events, as python objects
    :return: list of found errors. Empty list indicates not errors
    """
    errors = validate_structure_event_list(event_data)
    if errors:
        return errors

    for event in event_data['events']:
        errors_event = validate_event_adheres_to_schema(event_schema, event)
        errors.extend(errors_event)
    return errors


def validate_event_adheres_to_schema(event_schema: EventSchema, event: EventData) -> List[ErrorInfo]:
    """
    Validate that the event adheres to the EventSchema.

    This assumes that the event at least has the correct structure, i.e. if part of a list then
    validate_structure_event_list() should pass on it.

    Checks done:
        - event-type is part of event schema
        - all contexts have the correct attributes
        - all the contexts that are required by the event-type are present
    :param event_schema:
    :param event: Structural correct event.
    :return: list of found errors
    """
    event_name = event['_type']
    if not event_schema.is_valid_event_type(event_name):
        return [ErrorInfo(event, f'Unknown event: {event_name}')]

    errors = []

    # validate the event itself
    errors.extend(_validate_event_item(event_schema, event))

    # Validate that all of the event's contexts adhere to the schema of the specific contexts
    errors.extend(_validate_contexts(event_schema, event))
    # Validate that all of the event's required contexts are present
    errors.extend(_validate_required_contexts(event_schema, event))
    return errors


def _validate_required_contexts(event_schema: EventSchema, event: EventData) -> List[ErrorInfo]:
    """
    Validate that all of the event's required contexts are present
    :param event: event object
    :return: list of found errors. Will contain 1 item with all missing contexts if any are missing.
    """
    event_name = event['_type']
    global_contexts = event['global_contexts']
    location_stack = event['location_stack']
    required_context_types = event_schema.get_all_required_contexts(event_name)
    actual_types = set()
    for context in global_contexts:
        actual_types |= event_schema.get_all_parent_context_types(context['_type'])
    for context in location_stack:
        actual_types |= event_schema.get_all_parent_context_types(context['_type'])

    if not required_context_types.issubset(actual_types):
        error_info = ErrorInfo(
            event,
            f'Required contexts missing: {required_context_types - actual_types} '
            f'required_contexts: {required_context_types} - '
            f'found: {actual_types}'
        )
        return [error_info]
    return []


def _validate_contexts(event_schema: EventSchema, event: EventData) -> List[ErrorInfo]:
    """
    Validate that all of the event's contexts ad-here to the schema of the specific contexts.
    """
    global_contexts = event['global_contexts']
    location_stack = event['location_stack']
    errors = []
    for context in global_contexts:
        errors_context = _validate_context_item(event_schema=event_schema, context=context)
        if 'AbstractGlobalContext' not in event_schema.get_all_parent_context_types(context['_type']):
            errors.append(ErrorInfo(context, 'Not an instance of GlobalContext'))

        errors.extend(errors_context)
    for context in location_stack:
        errors_context = _validate_context_item(event_schema=event_schema, context=context)
        if 'AbstractLocationContext' not in event_schema.get_all_parent_context_types(context['_type']):
            errors.append(ErrorInfo(context, 'Not an instance of LocationContext'))

        errors.extend(errors_context)
    return errors


def _validate_context_item(event_schema: EventSchema, context) -> List[ErrorInfo]:
    """
    Check that a single context has the correct attributes
    :param context: objects
    :return: list of found errors
    """
    context_type = context['_type']
    # theoretically we could generate some json schema with if-then that we could just validate, without
    # having to select the right sub-schema here, but that would be very complex and not very readable.
    schema = event_schema.get_context_schema(context_type)
    if not schema:
        print(f'Unknown context {context_type}, ignoring')
        return []
    try:
        jsonschema.validate(instance=context, schema=schema)
    except ValidationError as exc:
        return [ErrorInfo(context, f'context validation failed: {exc}')]
    return []


def _validate_event_item(event_schema: EventSchema, event) -> List[ErrorInfo]:
    event_type = event['_type']
    schema = event_schema.get_event_schema(event_type=event_type)
    try:
        jsonschema.validate(instance=event, schema=schema)
    except ValidationError as exc:
        return [ErrorInfo(event, f'event validation failed {exc}')]

    return []


def validate_events_in_file(event_schema: EventSchema, filename: str) -> List[ErrorInfo]:
    """
    Read given filename, and validate the event data in that file.
    :param event_schema: EventSchema to use for validation
    :param filename: path of file to read
    :return: list of found errors
    """
    with open(filename) as file:
        event_data = json.loads(file.read())
    errors = validate_event_list(event_schema=event_schema, event_data=event_data['events'])
    if errors:
        print(f'\n{len(errors)} error(s) found:')
        for error in errors:
            print(f'error: {error[1]} object: {error[0]}')
        print(f'\nSummary: {len(errors)} error(s) found in {filename}')
    else:
        print(f'\nSummary: No errors found in {filename}')
    return errors


def validate_event_time(event: EventData, current_millis: int) -> List[ErrorInfo]:
    """
    Validate timestamps in event to check if it's not too old or too new
    :param event:
    :param current_millis:
    :return: [ErrorInfo], if any
    """
    max_delay = get_config_timestamp_validation().max_delay
    if max_delay and current_millis - event['time'] > max_delay:
        return [ErrorInfo(event, f'Event too old: {current_millis - event["time"]} > {max_delay}')]
    if event['time'] > current_millis:
        return [ErrorInfo(event, f'Event in the future: {event["time"]} > {current_millis}')]
    return []


def main():
    parser = argparse.ArgumentParser(description='Validate events')
    parser.add_argument('--schema-extensions-directory', type=str)
    parser.add_argument('filenames', type=str, nargs='+')
    args = parser.parse_args(sys.argv[1:])

    errors: Dict[str, List[ErrorInfo]] = {}
    filenames = args.filenames
    event_schema = get_event_schema(schema_extensions_directory=args.schema_extensions_directory)

    for filename in args.filenames:
        print(f'\nChecking {filename}')
        errors_file = validate_events_in_file(event_schema=event_schema,
                                              filename=filename)
        if errors_file:
            errors[filename] = errors_file
    if errors:
        print(f'\n\nCombined summary: Errors in {len(errors)} / {len(filenames)} file(s). '
              f'Files with errors: {list(errors.keys())}')
        exit(1)
    else:
        print(f'\n\nCombined summary: No errors found in {len(filenames)} file(s).')


if __name__ == '__main__':
    main()
