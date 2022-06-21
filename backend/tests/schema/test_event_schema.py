"""
Copyright 2021 Objectiv B.V.
"""
from copy import deepcopy

import pytest

from objectiv_backend.schema.event_schemas import EventSchema


# ### Below we test building a Schema object
def test_create_schema_empty():
    schema = EventSchema()
    assert schema.list_event_types() == []
    assert schema.list_context_types() == []
    assert schema.version == {}


def test_create_schema_extend():
    schema = EventSchema().get_extended_schema(_SIMPLE_BASE_SCHEMA)
    assert schema.list_event_types() == ['BaseEvent', 'Child2Event', 'ChildEvent', 'GrandChildEvent']
    assert schema.list_context_types() == ['AnotherContext', 'BaseContext', 'OtherContext']
    assert schema.version == {'test_schema': '1.0.0'}


def test_create_schema_extend_multiple():
    schema = EventSchema()\
        .get_extended_schema(_SIMPLE_BASE_SCHEMA)\
        .get_extended_schema(_EXTENSION_TO_SIMPLE_BASE_SCHEMA)
    assert schema.list_event_types() == \
           ['BaseEvent', 'Child2Event', 'ChildEvent', 'GrandChildEvent', 'GreatGrandChildEvent']
    assert schema.list_context_types() == ['AnotherContext', 'BaseContext', 'ExtraContext', 'OtherContext']
    expected_version = {
        'extension_to_test_schema': '0.5',
        'test_schema': '1.0.0'
    }
    assert schema.version == expected_version


def test_create_schema_event_cycles_error():
    schema_in = deepcopy(_SIMPLE_BASE_SCHEMA)
    # introduce cycle: ChildEvent -> GrandChildEvent -> ChildEvent -> ...
    schema_in['events']['ChildEvent']['parents'].append('GrandChildEvent')
    schema = EventSchema()
    with pytest.raises(ValueError, match='Cycle in event graph'):
        schema.get_extended_schema(schema_in)


def test_create_schema_event_reference_error():
    schema_in = deepcopy(_SIMPLE_BASE_SCHEMA)
    schema_in['events']['ChildEvent']['parents'].append('NonExistingEvent')
    schema = EventSchema()
    with pytest.raises(ValueError, match='Not a valid event_type NonExistingEvent'):
        schema.get_extended_schema(schema_in)


def test_create_schema_event_misnamed_error():
    schema_in = deepcopy(_SIMPLE_BASE_SCHEMA)
    schema_in['events']['wrong_event_name'] = schema_in['events']['BaseEvent']
    schema = EventSchema()
    with pytest.raises(ValueError, match='Invalid event name: wrong_event_name'):
        schema.get_extended_schema(schema_in)


def test_create_schema_context_cycles_error():
    schema_in = deepcopy(_SIMPLE_BASE_SCHEMA)
    # introduce cycle: ChildEvent -> GrandChildEvent -> ChildEvent -> ...
    schema_in['contexts']['BaseContext']['parents'] = ['OtherContext']
    schema = EventSchema()
    with pytest.raises(ValueError, match='Cycle in context graph'):
        schema.get_extended_schema(schema_in)


def test_create_schema_context_reference_error():
    schema_in = deepcopy(_SIMPLE_BASE_SCHEMA)
    schema_in['contexts']['BaseContext']['parents'] = ['NonExistingContext']
    schema = EventSchema()
    with pytest.raises(ValueError, match='Not a valid context_type NonExistingContext'):
        schema.get_extended_schema(schema_in)


def test_create_schema_context_misnamed_error():
    schema_in = deepcopy(_SIMPLE_BASE_SCHEMA)
    schema_in['contexts']['invalid_context_name'] = schema_in['contexts']['OtherContext']
    schema = EventSchema()
    with pytest.raises(ValueError, match='Invalid context name: invalid_context_name'):
        schema.get_extended_schema(schema_in)


def test_create_schema_event_reference_non_existing_context_error():
    schema_in = deepcopy(_SIMPLE_BASE_SCHEMA)
    schema_in['events']['ChildEvent']['requiresContext'].append('NonExistingContext')
    schema = EventSchema()
    with pytest.raises(ValueError,
                       match='^Contexts required by events are not defined .*NonExistingContext.*$'):
        schema.get_extended_schema(schema_in)


# ### Below we tests functions of an already created Schema object
def test_all_parent_event_types():
    schema = _get_schema()
    # todo: maybe come up with a better name that 'all_parent_even_types', a bit confusing that the type
    #    itself is also included. That's the behaviour we want, but not what the name implies.
    event_to_parents = {
        'BaseEvent':
            {'BaseEvent'},
        'ChildEvent':
            {'BaseEvent', 'ChildEvent'},
        'GrandChildEvent':
            {'BaseEvent', 'ChildEvent', 'Child2Event', 'GrandChildEvent'},
        'GreatGrandChildEvent':
            {'BaseEvent', 'ChildEvent', 'Child2Event', 'GrandChildEvent', 'GreatGrandChildEvent'},
    }
    for event_type, expected in event_to_parents.items():
        assert schema.get_all_parent_event_types(event_type) == expected


def test_all_required_contexts_for_event():
    schema = _get_schema()
    event_to_contexts = {
        'BaseEvent':
            {'BaseContext'},
        'ChildEvent':
            {'BaseContext'},
        'GrandChildEvent':
            {'BaseContext', 'OtherContext'},
        'GreatGrandChildEvent':
            {'BaseContext', 'OtherContext', 'ExtraContext'},
    }
    for event_type, expected in event_to_contexts.items():
        assert schema.get_all_required_contexts_for_event(event_type) == expected


def test_all_required_contexts_for_context():
    schema = _get_schema()

    context_to_contexts = {
        'BaseContext':
            {},
        'AnotherContext':
            {'OtherContext'}
    }
    # check for required contexts
    for context_type, expected in context_to_contexts.items():
        assert schema.get_all_required_contexts_for_context(context_type) == set(expected)

    context_to_contexts = {
        'AnotherContext':
            {'AnotherContext', 'BaseContext'}
    }
    # check for required contexts
    for context_type, expected in context_to_contexts.items():
        assert schema.get_all_required_contexts_for_context(context_type) != expected


def test_list_types():
    schema = _get_schema()
    assert schema.list_context_types() == ['AnotherContext', 'BaseContext', 'ExtraContext', 'OtherContext']


def test_all_parent_context_types():
    schema = _get_schema()
    # If we get a non-existing context we don't complain. Because in operation if we get more data (or
    # more contexts) than required then that's fine.
    # todo: check whether above is good idea. or should we put the leniency in another spot in the code?
    assert schema.get_all_parent_context_types('X') == {'X'}
    assert schema.get_all_parent_context_types('BaseContext') == {'BaseContext'}
    assert schema.get_all_parent_context_types('OtherContext') == {'BaseContext', 'OtherContext'}
    assert schema.get_all_parent_context_types('ExtraContext') == \
           {'BaseContext', 'OtherContext', 'ExtraContext'}


def test_all_child_context_types():
    schema = _get_schema()
    assert schema.get_all_child_context_types('X') == set()
    assert schema.get_all_child_context_types('BaseContext') == \
           {'AnotherContext', 'BaseContext', 'OtherContext', 'ExtraContext'}
    assert schema.get_all_child_context_types('OtherContext') == {'ExtraContext', 'OtherContext'}
    assert schema.get_all_child_context_types('ExtraContext') == {'ExtraContext'}


def test_get_context_schema():
    schema = _get_schema()
    base_context_json_schema = {
        'properties': {
            'id': {
                'type': 'string',
                'description': 'test id'
            }
        },
        'required': ['id'],
        'type': 'object'
    }
    extra_context_json_schema = {
        'properties': {
            'extra_property': {
                'type': 'string',
                'description': 'test extra property'
            },
            'id': {
                'type': 'string',
                'description': 'test id'
            },
            'other_property': {
                'type': 'number',
                'description': 'test other property'
            },
            'optional_property': {
                'type': ['string', 'null'],
                'description': 'this property is optional',
                'optional': True
            }
        },
        'required': ['extra_property', 'id', 'other_property'],
        'type': 'object'
    }

    assert schema.get_context_schema('BaseContext') == base_context_json_schema
    assert schema.get_context_schema('ExtraContext') == extra_context_json_schema


def test_optional_property():
    schema = _get_schema()

    other_context = schema.get_context_schema("OtherContext")

    # check optional property is there
    assert other_context['properties']['optional_property']

    # check optional property is not required
    assert other_context['required'] == ['id', 'other_property']


# ### Below are helper functions and test data
def _get_schema() -> EventSchema:

    return EventSchema()\
        .get_extended_schema(_SIMPLE_BASE_SCHEMA)\
        .get_extended_schema(_EXTENSION_TO_SIMPLE_BASE_SCHEMA)


_SIMPLE_BASE_SCHEMA = {
    "name": "test_schema",
    "version": {"test_schema": "1.0.0"},
    "comment": "Very simple schema for tests",
    "events": {
        "BaseEvent": {
            "parents": [],
            "requiresContext": ["BaseContext"],
            "description": "test base event"
        },
        "ChildEvent": {
            "parents": ["BaseEvent"],
            "requiresContext": [],
            "description": "test child event"
        },
        "Child2Event": {
            "parents": ["BaseEvent"],
            "requiresContext": ["OtherContext"],
            "description": "test child 2 event"
        },
        "GrandChildEvent": {
            "parents": ["ChildEvent", "Child2Event"],
            "requiresContext": [],
            "description": "test grand child event"
        },
    },
    "contexts": {
        "BaseContext": {
            "description": "test base context",
            "properties": {
                "id": {
                    "type": "string",
                    "description": "test id"
                }
            },

        },
        "OtherContext": {
            "parents": [
                "BaseContext"
            ],
            "description": "test other context",
            "properties": {
                "other_property": {
                    "type": "number",
                    "description": "test other property"
                },
                "optional_property": {
                    "type": "string",
                    "description": "this property is optional",
                    "optional": True
                }
            }
        },
        "AnotherContext": {
            "parents": ["BaseContext"],
            "description": "another test context which requires OtherCOntext",
            "requiresContext": ["OtherContext"]
        }
    }
}

_EXTENSION_TO_SIMPLE_BASE_SCHEMA = {
    "name": "extension_to_test_schema",
    "version": {"extension_to_test_schema": "0.5"},
    "comment": "Extension to test schema",
    "events": {
        "GreatGrandChildEvent": {
            "parents": ["GrandChildEvent"],
            "requiresContext": ["ExtraContext"],
            "description": "test great grand child event"
        },
    },
    "contexts": {
        "ExtraContext": {
            "parents": [
                "BaseContext",
                "OtherContext"
            ],
            "description": "test extra context",
            "properties": {
                "extra_property": {
                    "type": "string",
                    "description": "test extra property"
                }
            }
        }
    }
}
