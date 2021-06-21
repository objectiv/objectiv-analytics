"""
Copyright 2021 Objectiv B.V.
"""
import argparse
import json
import sys
from typing import List, Any, Dict, NamedTuple

import jsonschema
from jsonschema import ValidationError

from objectiv_backend.common.types import EventData
from objectiv_backend.schema.event_schemas import EventSchema, get_event_schema

EVENT_LIST_SCHEMA = {
    "type": "array",
    "items":  {
        "type": "object",
        "properties": {
            "event": {
                "type": "string"
            },
            # TODO: global_contexts and location_stack are identical for now but we could make this very strict
            "global_contexts": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "_context_type": {"type": "string"},
                    },
                    "required": ["_context_type"]
                }
            },
            "location_stack": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "_context_type": {"type": "string"},
                    },
                    "required": ["_context_type"]
                }
            },
            "time": {
                "type": "integer",
                # format: milliseconds since 1970-01-01 00:00:00
                # Data needs to be recent, but we allow a bit of slack because we might convert some
                # recent data for importing. Setting this minimum value should also catch situations where
                # we get timestamps in seconds instead of milliseconds
                "minimum": 1_577_836_800_000,  # 2020-01-01 00:00:00
            }
        },
        "required": ["event", "global_contexts", "location_stack"]  # TODO: make time a required field
    }
}


class ErrorInfo(NamedTuple):
    data: Any
    info: str


def validate_structure_event_list(event_data: Any) -> List[ErrorInfo]:
    """
    Checks that event_data is a list of events, that each event has the required fields, and that all
        contexts have the base required fields (id and _context_type).
    Does not perform any schema-dependent validation, e.g. doesn't check that the event type is valid,
    that an event has the right contexts, or that contexts have the right fields. For those checks call
    validate_event_adheres_to_schema on each individual event.
    :return: list of found errors. Empty list indicates not errors
    """
    try:
        jsonschema.validate(instance=event_data, schema=EVENT_LIST_SCHEMA)
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

    for event in event_data:
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
    :param event: Structural correct event.
    :return: list of found errors
    """
    event_name = event['event']
    if not event_schema.is_valid_event_type(event_name):
        return [ErrorInfo(event, f'Unknown event: {event_name}')]

    errors = []
    # Validate that all of the event's contexts adhere to the schema of the specific contexts
    errors.extend(_validate_contexts(event_schema, event))
    # Validate that all of the event's required contexts are present
    errors.extend(_validate_required_contexts(event_schema, event))
    return errors


def _validate_required_contexts(event_schema: EventSchema, event: Dict[str, Any]) -> List[ErrorInfo]:
    """
    Validate that all of the event's required contexts are present
    :param event: event object
    :return: list of found errors. Will contain 1 item with all missing contexts if any are missing.
    """
    event_name = event['event']
    global_contexts = event['global_contexts']
    location_stack = event['location_stack']
    required_context_types = event_schema.get_all_required_contexts(event_name)
    actual_context_types = set()
    for context in global_contexts:
        actual_context_types |= event_schema.get_all_parent_context_types(context['_context_type'])
    for context in location_stack:
        actual_context_types |= event_schema.get_all_parent_context_types(context['_context_type'])

    if not required_context_types.issubset(actual_context_types):
        error_info = ErrorInfo(
            event,
            f'Required contexts missing: {required_context_types - actual_context_types} '
            f'required_contexts: {required_context_types} - '
            f'found: {actual_context_types}'
        )
        return [error_info]
    return []


def _validate_contexts(event_schema: EventSchema, event: Dict[str, Any]) -> List[ErrorInfo]:
    """
    Validate that all of the event's contexts ad-here to the schema of the specific contexts.
    """
    global_contexts = event['global_contexts']
    location_stack = event['location_stack']
    errors = []
    for context in global_contexts:
        errors_context = _validate_context_item(event_schema=event_schema, context=context)
        errors.extend(errors_context)
    for context in location_stack:
        errors_context = _validate_context_item(event_schema=event_schema, context=context)
        errors.extend(errors_context)
    return errors


def _validate_context_item(event_schema: EventSchema, context) -> List[ErrorInfo]:
    """
    Check that a single context has the correct attributes
    :param context: objects
    :return: list of found errors
    """
    context_type = context['_context_type']
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


def validate_events_in_file(event_schema: EventSchema, filename: str) -> List[ErrorInfo]:
    """
    Read given filename, and validate the event data in that file.
    :param filename: path of file to read
    :return: list of found errors
    """
    with open(filename) as file:
        event_data = json.loads(file.read())
    errors = validate_event_list(event_schema=event_schema, event_data=event_data)
    if errors:
        print(f'\n{len(errors)} error(s) found:')
        for error in errors:
            print(f'error: {error[1]} object: {error[0]}')
        print(f'\nSummary: {len(errors)} error(s) found in {filename}')
    else:
        print(f'\nSummary: No errors found in {filename}')
    return errors


def main():
    parser = argparse.ArgumentParser(description='Validate events')
    parser.add_argument('--schema-extensions-directory', type=str)
    parser.add_argument('filenames', type=str, nargs='+')
    args = parser.parse_args(sys.argv[1:])

    errors: Dict[str, List[ErrorInfo]] = {}
    filenames = args.filenames
    event_schema = get_event_schema(schema_extensions_directory=args.schema_extensions_directory)

    print(f'Schema: {event_schema}')
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
