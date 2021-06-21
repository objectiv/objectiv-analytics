"""
Copyright 2021 Objectiv B.V.
"""
import json
import os
import re
import sys
from copy import deepcopy
from typing import Set, List, Dict, Any, Optional, Tuple

from objectiv_backend.common.types import EventType, ContextType

MAX_HIERARCHY_DEPTH = 100


class EventSubSchema:
    """
    Immutable sub-schema containing events, their inheritance hierarchy and required contexts for events.
    """

    EVENT_NAME_REGEX = r'^[A-Z][a-zA-Z0-9]*Event$'

    def __init__(self):
        """
        Create an empty EventSubSchema.
        Use extend_schema to add event types to the schema.
        """
        self.schema: Dict[EventType, Dict[str, list]] = {}
        # _compiled_* fields are derived fields that need to be calculated after self.schema is set.
        self._compiled_list_event_types: List[EventType] = []
        self._compiled_all_parents_and_required_contexts: \
            Dict[EventType, Tuple[Set[EventType], Set[ContextType]]] = {}

    def get_extended_schema(self, event_schema: Dict[str, Any]) -> 'EventSubSchema':
        """
        Extend the schema with the events in event_schema. Returns a new EventSubSchema, self is
        unmodified.

        :raises ValueError: in case the schema contains an internal inconsistency (e.g. a parent event
            doesn't exist).
        """
        schema = deepcopy(self.schema)
        for event_type, data in event_schema.items():
            # todo: move this check to schema check?
            if not re.match(self.EVENT_NAME_REGEX, event_type):
                raise ValueError(f'Invalid event name: {event_type}')
            if event_type not in schema:
                schema[event_type] = {'parents': [], 'requiresContext': []}
            schema[event_type]['parents'].extend(data['parents'])
            schema[event_type]['requiresContext'].extend(data['requiresContext'])
        event_sub_schema = EventSubSchema()
        event_sub_schema.schema = schema
        event_sub_schema._compile()
        return event_sub_schema

    def _compile(self):
        """
        1) Pre calculate the return values of list_event_types(), get_all_parent_event_types(), and
        get_all_required_contexts.
        2) Makes sure the event hierarchy has no cycles
        Must be called after the schema has changed.
        """
        # pre-calculate all values
        self._compiled_list_event_types = sorted(self.schema.keys())
        self._compiled_all_parents_and_required_contexts = {}
        for event_type in self._compiled_list_event_types:
            self._compile_parents_and_contexts(event_type)

    def _compile_parents_and_contexts(
            self,
            event_type: EventType,
            count=MAX_HIERARCHY_DEPTH
    ) -> Tuple[Set[EventType], Set[ContextType]]:
        """
        For a given event-type give:
        1) all event-types that this type is, i.e. the type itself and all its parents
        2) all context-types that are required for this type (and it's parent types)

        In the process this also stores this information in the _compiled_all_parents_and_required_contexts
        field for the given event-type and all its parent types.
        Additionally this function checks that the event-hierarchy:
            1) does not contain cycles, nor is too deep
            2) the parent event references exist
        """
        if event_type in self._compiled_all_parents_and_required_contexts:
            return self._compiled_all_parents_and_required_contexts[event_type]

        if count == 0:
            # This is a very crude way to check for cycles, but it works.
            raise ValueError(f'Cycle in event graph, or hierarchy too deep. At event type {event_type}')

        if not self.is_valid_event_type(event_type):
            raise ValueError(f'Not a valid event_type {event_type}')

        event_types: Set[EventType] = {event_type}
        context_types: Set[ContextType] = set(self.schema[event_type].get('requiresContext', []))
        parents: List[EventType] = self.schema[event_type].get('parents', [])
        for parent in parents:
            parent_event_types, parent_context_types = \
                self._compile_parents_and_contexts(event_type=parent, count=count - 1)
            event_types |= parent_event_types
            context_types |= parent_context_types

        result = event_types, context_types
        self._compiled_all_parents_and_required_contexts[event_type] = result
        return result

    def list_event_types(self) -> List[str]:
        """ Give a alphabetically sorted list of all event-types. """
        return self._compiled_list_event_types

    def get_all_parent_event_types(self, event_type: EventType) -> Set[EventType]:
        """
        Given an event_type, give a set with that event_type and all its parent event_types.
        :param event_type: event type. Must be a valid event_type
        :return: set of event_types; an event_type is a string with the name of that event
        """
        if not self.is_valid_event_type(event_type):
            raise ValueError(f'Not a valid event_type {event_type}')
        return self._compiled_all_parents_and_required_contexts[event_type][0]

    def get_all_required_contexts(self, event_type: EventType) -> Set[ContextType]:
        """
        Get all contexts that are required by the given event. This includes context types that are
        required by the type's parent events.
        :param event_type: event type. Must be a valid event_type
        :return: set of context_types; a context_type is a string with the name of that context
        """
        if not self.is_valid_event_type(event_type):
            raise ValueError(f'Not a valid event_type {event_type}')
        return self._compiled_all_parents_and_required_contexts[event_type][1]

    def is_valid_event_type(self, event_type: EventType) -> bool:
        return event_type in self.schema


class ContextSubSchema:
    """
    Immutable sub-schema containing contexts, their inheritance hierarchy, their properties and
    their attributes.
    """

    def __init__(self):
        """
        Create an empty ContextSubSchema.
        Use extend_schema to add event types to the schema.
        """
        self.schema: Dict[str, Any] = {}
        # _compiled_* fields are derived fields that need to be calculated after self.schema is set.
        self._compiled_list_context_types = []
        self._compiled_all_parent_context_types = {}
        self._compiled_all_child_context_types = {}

    CONTEXT_NAME_REGEX = r'^[A-Z][a-zA-Z0-9]*Context$'

    def __str__(self) -> str:
        return json.dumps(self.schema, indent=4)

    def get_extended_schema(self, context_schema_extension) -> 'ContextSubSchema':
        """
        Create a new context schema that combines the current schema with the schema extension

        TODO: more, and better documentation
        TODO: build smarter data structures, such that functions below are simple lookups.
        """
        schema = deepcopy(self.schema)
        for context_type, data in context_schema_extension.items():
            # todo: move this check to schema check?
            if not re.match(self.CONTEXT_NAME_REGEX, context_type):
                raise ValueError(f'Invalid context name: {context_type}')

            if context_type not in schema:
                schema[context_type] = {"parents": [], "properties": {}}

            schema[context_type]["parents"].extend(data.get("parents", []))

            for property_type, property_data in data.get("properties", {}).items():
                if property_type not in schema[context_type]["properties"]:
                    schema[context_type]["properties"][property_type] = {}
                existing_property = schema[context_type]["properties"][property_type]
                for sub_property_name, sub_property_value in property_data.items():
                    if (sub_property_name in existing_property and
                            sub_property_value != existing_property[sub_property_name]):
                        raise ValueError(f'Cannot change a property of an existing property. '
                                         f'Redefining value of {sub_property_name} of {property_type}')
                    existing_property[sub_property_name] = sub_property_value
        context_schema = ContextSubSchema()
        context_schema.schema = schema
        context_schema._compile()
        return context_schema

    def _compile(self):
        """
        1) Pre calculate the return values of list_context_types(), get_all_parent_context_types(),
            and get_all_child_context_types().
        2) Makes sure the event hierarchy has no cycles, and all parent-reference exist.
        Must be called after the schema has changed.
        """
        self._compiled_list_context_types = sorted(self.schema.keys())
        self._compiled_all_parent_context_types = {}
        self._compiled_all_child_context_types = {}
        # Calculate parent relations, and do some basic checks on graph
        for context_type in self._compiled_list_context_types:
            self._compile_parent_context_types(context_type)

        # Calculate child relations based on parent relations
        for context_type in self._compiled_list_context_types:
            children: Set[str] = set()
            for ct in self._compiled_list_context_types:
                if context_type in self._compiled_all_parent_context_types[ct]:
                    children.add(ct)
            self._compiled_all_child_context_types[context_type] = children

    def _compile_parent_context_types(self,
                                      context_type: ContextType,
                                      count=MAX_HIERARCHY_DEPTH) -> Set[ContextType]:
        """
        * Give the parent context-types of the given context-type (including the given type itself).
        * Fill self._compiled_all_parent_context_types for the explored context_types.
        * Check for two kind of type-graph errors: 1) non-existing parent context references, 2) cycles
        """
        if context_type in self._compiled_all_parent_context_types:
            return self._compiled_all_parent_context_types[context_type]

        if count == 0:
            # This is a very crude way to check for cycles, but it works.
            raise ValueError(f'Cycle in context graph, or hierarchy too deep. '
                             f'At context type {context_type}')

        if context_type not in self.schema:
            raise ValueError(f'Not a valid context_type {context_type}')

        result: Set[ContextType] = {context_type}
        parents: List[ContextType] = self.schema[context_type].get('parents', [])
        for parent in parents:
            result |= self._compile_parent_context_types(parent, count=count-1)
        self._compiled_all_parent_context_types[context_type] = result
        return result

    def list_context_types(self) -> List[ContextType]:
        """ Give a alphabetically sorted list of all context-types. """
        return self._compiled_list_context_types

    def get_all_parent_context_types(self, context_type: ContextType) -> Set[ContextType]:
        """
        Given a context_type, give a set with that context_type and all its parent context_types
        """
        return self._compiled_all_parent_context_types.get(context_type, {context_type})

    def get_all_child_context_types(self, context_type: ContextType) -> Set[ContextType]:
        """
        Given a context_type, give a set with that context_type and all its child context_types
        """
        return self._compiled_all_child_context_types.get(context_type, set())

    def get_context_schema(self, context_type: ContextType) -> Optional[Dict[str, Any]]:
        """
        Give the json-schema for a specific context_type, or None if the context type doesn't exist.
        """
        if context_type not in self.schema:
            return None
        all_classes = self.get_all_parent_context_types(context_type)
        properties = {}
        for klass in all_classes:
            class_properties = deepcopy(self.schema[klass].get("properties", {}))
            for key, value in class_properties.items():
                properties[key] = deepcopy(value)
        schema = {
            "type": "object",
            "properties": properties,
            "required": sorted(properties.keys())
        }
        return schema


class EventSchema:
    """
    Immutable schema containing events, their contexts, and version information.
    """

    def __init__(self):
        """
        Create an empty EventSchema.
        Use extend_schema to add types to the schema.
        """
        self.version = {}
        self.events = EventSubSchema()
        self.contexts = ContextSubSchema()

    def get_extended_schema(self, schema: Dict[str, Any]) -> 'EventSchema':
        """
        Extend the schema with the events and contexts in schema. Returns a new EventSchema, self is
        unmodified.

        Allowed extensions for events:
            * adding new events
            * adding parents to an existing event
            * adding contexts to the requiresContext field of an existing event
        Allowed extensions for contexts:
            * adding new contexts
            * adding parents to an existing context
            * adding properties to an existing context
            * adding sub-properties to an existing context (e.g. a "minimum" field for an integer)
        """
        events = deepcopy(self.events)
        contexts = deepcopy(self.contexts)
        version = deepcopy(self.version)

        events = events.get_extended_schema(schema['events'])
        contexts = contexts.get_extended_schema(schema['contexts'])
        version.update(schema['version'])
        # todo: separate version merging, and do some validation on this
        # extension_name = event_schema['name']
        # if extension_name in self.schema['version']:
        #     raise ValueError(f'Duplicate schema name. '
        #                      f'Already a version of "{extension_name}" loaded')

        # Validation: The EventSubSchema and ContextSubSchema are responsible for validating internal
        # consistency of the sub-schemes. Here we validate the inter-schema consistency
        self._validate_events_required_contexts(events, contexts)

        result = EventSchema()
        result.events = events
        result.contexts = contexts
        result.version = version
        return result

    @staticmethod
    def _validate_events_required_contexts(events: EventSubSchema, contexts: ContextSubSchema):
        """
        Check that all 'requiredContexts' defined in events schema exist in the contexts schema.
        :raise ValueError: in case a required context is missing.
        """
        all_required_contexts = set()
        for event_type in events.list_event_types():
            all_required_contexts |= events.get_all_required_contexts(event_type)
        all_contexts = contexts.list_context_types()
        missing_contexts = all_required_contexts - set(all_contexts)
        if missing_contexts:
            raise ValueError(f'Contexts required by events are not defined in context sub schema: '
                             f'{missing_contexts}')

    def __str__(self) -> str:
        """ Json representation of this data-schema. """
        schema_obj = {
            "version": self.version,
            "events": self.events.schema,
            "contexts": self.contexts.schema
        }
        return json.dumps(schema_obj, indent=4)

    def list_event_types(self) -> List[EventType]:
        """ Give a alphabetically sorted list of all event-types. """
        return self.events.list_event_types()

    def get_all_parent_event_types(self, event_type: EventType) -> Set[EventType]:
        """
        Given an event_type, give a set with that event_type and all its parent event_types.
        :param event_type: event type. Must be a valid event_type
        :return: set of event_types
        """
        return self.events.get_all_parent_event_types(event_type=event_type)

    def get_all_required_contexts(self, event_type: EventType) -> Set[ContextType]:
        return self.events.get_all_required_contexts(event_type=event_type)

    def is_valid_event_type(self, event_type: EventType) -> bool:
        return self.events.is_valid_event_type(event_type=event_type)

    def list_context_types(self) -> List[ContextType]:
        return self.contexts.list_context_types()

    def get_all_parent_context_types(self, context_type: ContextType) -> Set[ContextType]:
        return self.contexts.get_all_parent_context_types(context_type=context_type)

    def get_all_child_context_types(self, context_type: ContextType) -> Set[ContextType]:
        return self.contexts.get_all_child_context_types(context_type=context_type)

    def get_context_schema(self, context_type: ContextType) -> Optional[Dict[str, Any]]:
        return self.contexts.get_context_schema(context_type=context_type)


def get_event_schema(schema_extensions_directory: Optional[str]) -> EventSchema:
    """
    Get the event schema.

    The schema is based on base_schema.json and the schema files in the optional
    schema_extension_directory.
    Files in the extension directory qualify for loading if their name matches [a-z0-9_]+\\.json.
    The files are loaded in alphabetical order.

    :param schema_extensions_directory: optional directory path.
    """
    base_schema_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'base_schema.json')
    files_to_load = [base_schema_path]

    if schema_extensions_directory:
        all_filenames = sorted(os.listdir(schema_extensions_directory))
        for filename in all_filenames:
            if not re.match(r'[a-z0-9_]+\.json', filename):
                print(f'Ignoring non-schema file: {filename}', file=sys.stderr)
                continue
            files_to_load.append(os.path.join(schema_extensions_directory, filename))

    schema_jsons = []
    for filepath in files_to_load:
        with open(filepath, mode='r') as file:
            raw_data = file.read()
        try:
            schema = json.loads(raw_data)
        except ValueError as exc:
            raise Exception(f'Schema file does not contain valid json {filepath}') from exc
        # todo: schema validation
        schema_jsons.append(schema)

    event_schema = EventSchema()
    for schema_json in schema_jsons:
        event_schema = event_schema.get_extended_schema(schema_json)
    return event_schema
