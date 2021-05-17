"""
Copyright 2021 Objectiv B.V.
"""
import json
from copy import deepcopy
from typing import Optional, Any, Dict, Set, List

CONTEXT_META = {
    "AbstractContext": {
        "properties": {
            "id": {"type": "string"}
        }
    },
    "AbstractLocationContext": {
        "parents": ["AbstractContext"]
    },
    "AbstractGlobalContext": {
        "parents": ["AbstractContext"]
    },
    "SectionContext": {
        "parents": ["AbstractLocationContext"]
    },
    "WebDocumentContext": {
        "parents": ["SectionContext"],
        "properties": {
            "url": {"type": "string"}
        }
    },
    "ScreenContext": {
        "parents": ["SectionContext"],
        "properties": {
            "screen": {"type": "string"}
        }
    },
    "ExpandableSectionContext": {
        "parents": ["SectionContext"],
    },
    "MediaPlayerContext": {
        "parents": ["SectionContext"],
    },
    "NavigationContext": {
        "parents": ["SectionContext"],
    },
    "OverlayContext": {
        "parents": ["SectionContext"],
    },

    "ItemContext": {
        "parents": ["AbstractLocationContext"],
    },
    "InputContext": {
        "parents": ["ItemContext"]
    },
    "ActionContext": {
        "parents": ["ItemContext"],
        "properties": {
            # TODO ideally `path` and `text` should be wrapped in a `anyOf` operator
            "path": {"type": "string"},
            "text": {"type": "string"},
        }
    },
    "ButtonContext": {
        "parents": ["ActionContext"],
    },
    "LinkContext": {
        "parents": ["ActionContext"],
    },
    "DeviceContext": {
        "parents": ["AbstractGlobalContext"],
        "properties": {
            "user-agent": {"type": "string"}
        }
    },
    "ErrorContext": {
        "parents": ["AbstractGlobalContext"],
        "properties": {
            "message": {"type": "string"}
        }
    },
    "CookieIdContext": {
        "parents": ["AbstractGlobalContext"],
        "properties": {
            # TODO: validate that this is a UUID
            "cookie_id": {"type": "string"},
        }
    },
    "SessionContext": {
        "parents": ["AbstractGlobalContext"],
        "properties": {
            "hitNumber": {"type": "integer"},
        }
    },
    "HttpContext": {
        "parents": ["AbstractGlobalContext"],
        "properties": {
            "host": {"type": "string"},
            "user-agent": {"type": "string"},
            # "referer": {"type": "string"},  # TODO: allow optional fields
            "remote_addr": {"type": "string"}
        }
    },
    "ABTestContext": {
        "parents": ["AbstractGlobalContext"],
        "properties": {
            "variant": {"type": "string"}
        }
    },
    "OptimizeContext": {
        "parents": ["ABTestContext"],
        "properties": {
            "propertyId": {"type": "string"}
        }
    }
}


class ContextSchema:
    def __init__(self, context_schema_extension: Dict[str, Any]):
        """

        :param context_schema_extension: Allowed extensions:
            * adding new contexts
            * adding parents to an existing context
            * adding properties to an existing context
            * adding sub-properties to an existing context (e.g. a "minimum" field for an integer)
        """
        self.schema = deepcopy(CONTEXT_META)
        for context_type, data in context_schema_extension.items():

            if context_type not in self.schema:
                self.schema[context_type] = {"parents": [], "properties": {}}

            self.schema[context_type]["parents"].extend(data.get("parents", []))

            for property_type, property_data in data.get("properties", {}).items():
                if property_type not in self.schema[context_type]["properties"]:
                    self.schema[context_type]["properties"][property_type] = {}
                existing_property = self.schema[context_type]["properties"][property_type]
                for sub_property_name, sub_property_value in property_data.items():
                    if (sub_property_name in existing_property and
                            sub_property_value != existing_property[sub_property_name]):
                        raise ValueError(f'Cannot change a property of an existing property. '
                                         f'Redefining value of {sub_property_name} of {property_type}')
                    existing_property[sub_property_name] = sub_property_value

    def __str__(self) -> str:
        return json.dumps(self.schema, indent=4)

    def list_context_types(self) -> List[str]:
        """ Give a alphabetically sorted list of all context-types. """
        return sorted(self.schema.keys())

    def get_all_parent_context_types(self, context_type: str) -> Set[str]:
        """
        Given a context_type, give a set with that context_type and all its parent context_types
        """
        result: Set[str] = {context_type}
        parents: List[str] = self.schema.get(context_type, {}).get("parents", [])
        for parent in parents:
            result |= self.get_all_parent_context_types(parent)
        return result

    def get_all_child_context_types(self, context_type: str) -> Set[str]:
        """
        Given a context_type, give a set with that context_type and all its child context_types
        """
        result: Set[str] = set()
        for ct in self.list_context_types():
            if context_type in self.get_all_parent_context_types(ct):
                result.add(ct)
        return result

    def get_context_schema(self, context_type: str) -> Optional[Dict[str, Any]]:
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
