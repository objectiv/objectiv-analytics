"""
Copyright 2021 Objectiv B.V.
"""
import argparse
import json
import sys
from typing import List, Any, Dict, NamedTuple, Set

from objectiv_backend.schema.event_schemas import EventSchema, get_event_schema
from objectiv_backend.schema.validate_events import get_event_list_schema


class SchemaDefinitionTuple(NamedTuple):
    schema: Dict[str, Any]
    definitions: Dict[str, Any]


def generate_json_schema(event_schema: EventSchema) -> Dict[str, Any]:
    sub_schemas = [
        get_schema_base_properties(),
        get_schema_event_required_contexts(event_schema=event_schema),
        get_schema_context_validation(event_schema=event_schema)
    ]

    combined_definitions = _combine_definition(sub_schemas)
    combined = {
        "allOf": [sub_schema.schema for sub_schema in sub_schemas],
        "definitions": combined_definitions
    }
    return combined


def _combine_definition(schema_definitions: List[SchemaDefinitionTuple]) -> Dict[str, Any]:
    """
    Get the combined definitions from all schema_definitions.
    Will give an error if there are any conflicting definitions.
    """
    overlap: Set[str] = set()
    for sd in schema_definitions:
        overlap &= set(sd.definitions.keys())
    if overlap:
        raise ValueError(f'Non-unique keys in the definitions: {overlap}')

    combined_definitions = {}
    for sd in schema_definitions:
        for key, value in sd.definitions.items():
            combined_definitions[key] = value
    return combined_definitions


def get_schema_base_properties() -> SchemaDefinitionTuple:
    """
    Return a json-schema to validate that the data is a list of events, and each event has the base
    properties (event and contexts) and that they are of the right type. Also check that each context
    has the properties id and _type.
    """
    return SchemaDefinitionTuple(
        schema=get_event_list_schema(),
        definitions={}
    )


def get_schema_context_validation(event_schema: EventSchema) -> SchemaDefinitionTuple:
    """
    Return a json-schema to validate that all contexts:
        1) Are Contexts that are part of the schema
        2) Have the properties as defined in the schema
    """
    references = []
    definitions = {}
    for context_type in event_schema.list_context_types():
        definition = event_schema.get_context_schema(context_type)
        # help mypy; we are iterating result of list_context_types, so definition should exist
        assert definition is not None
        definition["properties"]["_type"] = {"type": "string", "const": context_type}
        definitions[context_type] = definition
        references.append({"$ref":  f"#/definitions/{context_type}"})
    schema = {
        "type": "array",
        "items":  {
            "type": "object",
            "properties": {
                "event": {
                    "type": "string"
                },
                "contexts": {
                    "type": "array",
                    "items": {
                        "oneOf": references
                    }
                }
            },
            "required": ["event", "contexts"]
        }
    }
    return SchemaDefinitionTuple(schema=schema, definitions=definitions)


def get_schema_event_required_contexts(event_schema: EventSchema) -> SchemaDefinitionTuple:
    """
    Return a json-schema to validate that all events have the required contexts.
    Only checks the context by _type (=name), doesn't check that the contexts themselves are
    correct.
    """
    definitions = {}
    # For each event-type we'll generate a definition that will match that exact-type, and will prescribe
    # which contexts it must have
    for event_type in event_schema.list_event_types():
        contexts_requirements = []
        for context in event_schema.get_all_required_contexts_for_event(event_type):
            # For each required context we add the below fragment, as part of all 'allOf' clause.
            # This will make sure that all required contexts are present. Note that it is not needed to
            # match the exact required context-type, it can also be a child of the required context-type.
            child_contexts = sorted(event_schema.get_all_child_context_types(context))
            contexts_requirements.append(
                {
                    "type": "array",
                    "contains": {
                        "type": "object",
                        "properties": {
                            "_type": {
                                "type": "string",
                                "enum": child_contexts,
                            }
                        },
                        "required": ["_type"]
                    }
                }
            )
        definitions[event_type] = {
            "type": "object",
            "properties": {
                "event": {
                    "type": "string",
                    "const": event_type
                },
                "contexts": {
                    "allOf": contexts_requirements
                }
            },
            "required": ["event", "contexts"]
        }
    references = [{"$ref":  f"#/definitions/{event_type}"}
                  for event_type in event_schema.list_event_types()]
    schema = {
        "type": "array",
        "items": {
            "oneOf": references
        },
    }
    return SchemaDefinitionTuple(schema=schema, definitions=definitions)


def main():
    parser = argparse.ArgumentParser(description='Create json schema files')
    parser.add_argument('--schema-extensions-directory', type=str)
    args = parser.parse_args(sys.argv[1:])

    event_schema = get_event_schema(schema_extensions_directory=args.schema_extensions_directory)
    # todo: debug - remove next line and uncomment following
    #print(event_schema)
    json_schema = generate_json_schema(event_schema)
    print(json.dumps(json_schema, indent=4))


if __name__ == '__main__':
    main()
