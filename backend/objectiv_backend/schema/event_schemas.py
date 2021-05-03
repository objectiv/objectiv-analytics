"""
Copyright 2021 Objectiv B.V.
"""
import json
from copy import deepcopy
from typing import Set, List, Dict, Any, Optional

import json

from objectiv_backend.schema.context_schemas import ContextSchema

DEFAULT_SCHEMA = {
    "AbstractEvent": {
        "parents": [],
        "requiresContext": ["AbstractContext"]
    },
    "NonInteractiveEvent": {
        "parents": ["AbstractEvent"],
        "requiresContext": [],
    },
    "DocumentLoadedEvent": {
        "parents": ["NonInteractiveEvent"],
        "requiresContext": ["WebDocumentContext"],
    },
    "URLChangeEvent": {
        "parents": ["NonInteractiveEvent"],
        "requiresContext": ["WebDocumentContext"],
    },
    "ApplicationLoadedEvent": {
        "parents": ["NonInteractiveEvent"],
        "requiresContext": ["SectionContext"],
    },
    "SectionVisibleEvent": {
        "parents": ["NonInteractiveEvent"],
        "requiresContext": ["SectionContext"],
    },
    "SectionHiddenEvent": {
        "parents": ["NonInteractiveEvent"],
        "requiresContext": ["SectionContext"],
    },
    "VideoEvent": {
        "parents": ["NonInteractiveEvent"],
        "requiresContext": ["MediaPlayerContext"],
    },
    "VideoLoadEvent": {
        "parents": ["VideoEvent"],
        "requiresContext": [],
    },
    "VideoStartEvent": {
        "parents": ["VideoEvent"],
        "requiresContext": [],
    },
    "VideoStopEvent": {
        "parents": ["VideoEvent"],
        "requiresContext": [],
    },
    "VideoPauseEvent": {
        "parents": ["VideoEvent"],
        "requiresContext": [],
    },
    "InteractiveEvent": {
        "parents": ["AbstractEvent"],
        "requiresContext": ["SectionContext"]
    },
    "ClickEvent": {
        "parents": ["InteractiveEvent"],
        "requiresContext": [],
    },
    "InputChangeEvent": {
        "parents": ["InteractiveEvent"],
        "requiresContext": ["InputContext"],
    },
}


class EventSchema:
    def __init__(self,
                 event_schema_extension: Dict[str, Any],
                 context_schema_extension: Dict[str, Any]
                 ):
        """
        EventSchema, including the ContextSchema

        :param event_schema_extension: Allowed extensions:
            * adding new events
            * adding parents to an existing event
            * adding contexts to the requiresContext field of an existing event
        :param context_schema_extension: Allowed extensions:
            * adding new contexts
            * adding parents to an existing context
            * adding properties to an existing context
            * adding sub-properties to an existing context (e.g. a "minimum" field for an integer)
        """
        # TODO: efficiency, both this class and context_schema.py could calculate most function results at
        #       init-time which would be much more efficient.
        # TODO: ensure schema_extension is validated.
        self.schema = deepcopy(DEFAULT_SCHEMA)
        self.context_schema = ContextSchema(context_schema_extension)
        for event_type, data in event_schema_extension.items():
            if event_type not in self.schema:
                self.schema[event_type] = {"parents": [], "requiresContext": []}
            self.schema[event_type]["parents"].extend(data["parents"])
            self.schema[event_type]["requiresContext"].extend(data["requiresContext"])

    def __str__(self) -> str:
        event_schema_str = json.dumps(self.schema, indent=4)
        return f'\n' \
               f'Events: {event_schema_str}\n' \
               f'Contexts: {self.context_schema}\n'

    def list_event_types(self) -> List[str]:
        """ Give a alphabetically sorted list of all event-types. """
        return sorted(self.schema.keys())

    def get_all_parent_event_types(self, event_type: str) -> Set[str]:
        """
        Given an event_type, give a set with that event_type and all its parent event_types.
        :param event_type: event type. Must be a valid event_type
        :return: set of event_types
        """
        if not self.is_valid_event_type(event_type):
            raise ValueError(f'Not a valid event_type {event_type}')
        result: Set[str] = {event_type}
        parents: List[str] = self.schema[event_type].get("parents", [])
        for parent in parents:
            result |= self.get_all_parent_event_types(parent)
        return result

    def get_all_required_contexts(self, event_type: str) -> Set[str]:
        """
        Get all contexts that are required by the given event. This includes context types that are
        required by the type's parent events.
        :param event_type: event type. Must be a valid event_type
        :return: set of context_types
        """
        if not self.is_valid_event_type(event_type):
            raise ValueError(f'Not a valid event_type {event_type}')
        klasses = self.get_all_parent_event_types(event_type)
        result = set()
        for klass in klasses:
            result |= set(self.schema[klass].get("requiresContext", []))
        return result

    def is_valid_event_type(self, event_type: str) -> bool:
        return event_type in self.schema

    def list_context_types(self) -> List[str]:
        return self.context_schema.list_context_types()

    def get_all_parent_context_types(self, context_type: str) -> Set[str]:
        return self.context_schema.get_all_parent_context_types(context_type=context_type)

    def get_all_child_context_types(self, context_type: str) -> Set[str]:
        return self.context_schema.get_all_child_context_types(context_type=context_type)

    def get_context_schema(self, context_type: str) -> Optional[Dict[str, Any]]:
        return self.context_schema.get_context_schema(context_type=context_type)


def get_event_schema(event_schema_extension_filename: Optional[str],
                     context_schema_extension_filename: Optional[str]) -> EventSchema:
    """
    Get the event schema
    :param event_schema_extension_filename: optional filename for data to extend the event-schema
    :param context_schema_extension_filename: optional filename for data to extend the context-schema
    """
    event_schema_extension_data = {}
    if event_schema_extension_filename:
        with open(event_schema_extension_filename) as file:
            event_schema_extension_data = json.loads(file.read())
    context_schema_extension_data = {}
    if context_schema_extension_filename:
        with open(context_schema_extension_filename) as file:
            context_schema_extension_data = json.loads(file.read())
    event_schema = EventSchema(event_schema_extension=event_schema_extension_data,
                               context_schema_extension=context_schema_extension_data)
    return event_schema
