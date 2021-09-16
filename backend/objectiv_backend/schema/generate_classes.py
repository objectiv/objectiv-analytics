from typing import List, Dict, Any
import re

from objectiv_backend.common.config import get_collector_config


def get_type(property_description: Dict[str, Any]) -> str:
    """
    Translate (json)schema property type to something Python understands
    :param property_description: from schema
    :return: string containing Python type
    """
    type_name = property_description['type']

    abstract_type = ''
    if 'items' in property_description and 'type' in property_description['items']:
        abstract_type = property_description['items']['type']
    if type_name == 'array':
        return f'List[{abstract_type}]'
    if type_name == 'object':
        return 'Dict[str, Any]'
    if type_name == 'string':
        return 'str'
    if type_name == 'integer':
        return 'int'
    return 'str'


def get_parents(class_name: str, parent_mapping: Dict[str, List[str]]) -> List[str]:
    """
    Recursively resolve all parents (ancestry) of class_name
    :param class_name: class to resolve
    :param parent_mapping: mapping of class_name -> parents
    :return: List[str], list of parent classes
    """
    parents: List[str] = parent_mapping[class_name]

    for parent in parent_mapping[class_name]:
        parents = [*parents, *get_parents(parent, parent_mapping)]

    return parents


def get_parent_list(objects: Dict[str, Dict[str, Any]]) -> Dict[str, List[str]]:
    """
    Create list containing full ancestry of all classes
    :param objects:
    :return: dictionary with a list of ancestors per object
    """
    # first create a list of parent per obj
    parent_mapping: Dict[str, List[str]] = {}
    for obj_name, obj in objects.items():
        parent_mapping[obj_name] = obj['parents']

    parent_list: Dict[str, List[str]] = {}
    for klass in parent_mapping.keys():
        parent_list[klass] = get_parents(
            class_name=klass, parent_mapping=parent_mapping)

    return parent_list


def get_all_properties(object_list: List[str], objects: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """
    returns a dictionary containing properties of all objects in the list. Can be used to resolve all (inherited)
    properties of an object
    :param object_list: List of all objects in the ancestry
    :param objects:
    :return: dictionary of properties
    """
    properties: Dict[str, Dict[str, Any]] = {}
    for obj in object_list:
        if 'properties' in objects[obj]:
            properties.update(objects[obj]['properties'])

    return properties


def get_event_factory(objects: Dict[str, dict]) -> List[str]:
    """
    Generate very basic factory to be able to load events
    :param objects:
    :return: str - function to instantiate classes
    """
    factory: List[str] = [
        'def make_event(_type: str, **kwargs) -> AbstractEvent:']
    for obj_name, obj in objects.items():
        factory.append(f'    if _type == "{obj_name}":\n'
                       f'        return {obj_name}(**kwargs)')
    factory.append(f'    return AbstractEvent(**kwargs)')
    return factory


def get_context_factory(objects: Dict[str, dict]) -> List[str]:
    """
    Generate basic factory to create context instances
    :param objects:
    :return: str - function to instantiate classes
    """
    factory: List[str] = [
        'def make_context(_type: str, **kwargs) -> AbstractContext:']
    for obj_name, obj in objects.items():
        factory.append(f'    if _type == "{obj_name}":\n'
                       f'        return {obj_name}(**kwargs)')
    factory.append(f'    return AbstractContext(**kwargs)')
    return factory


def get_event_maker() -> str:
    """
    Generate factory to create and hydrate event (AbstractEvent) object
    :return:
    """
    return (f"def make_event_from_dict(obj: Dict[str, Any]) -> AbstractEvent:\n"
            f"    if not ('_type' in obj and 'location_stack' in obj and 'global_contexts' in obj):\n"
            f"        raise Exception('missing arguments')\n"
            f"    obj['location_stack'] = [make_context(**c) for c in obj['location_stack']]\n"
            f"    obj['global_contexts'] = [make_context(**c) for c in obj['global_contexts']]\n\n"
            f"    return make_event(**obj)\n")


def indent_lines(code: str, level: int, spaces: int = 4):
    """
    indentation helper function. Add spaces in front of every line of code
    :param code: string, code to be indented
    :param level: indentation level
    :param spaces: # of spaces per level
    :return: indented string
    """
    width = level * spaces
    lines = code.split('\n')

    return '\n'.join([line.rjust(width + len(line), ' ') for line in lines])


def get_constructor_description(property_meta: Dict[str, dict]) -> str:
    """
    Build docstring for class constructor. Should be of the form:
    :param property_meta <property_meta>: <property_description>
    :return: str - python comment
    """
    params = [f':param {name}: \n{indent_lines(meta["description"], level=1)}'
              for name, meta in property_meta.items()]

    return indent_lines(f'"""\n' + '\n'.join(params) + f'\n"""', level=2)


def get_args_string(property_meta: Dict[str, dict]) -> str:
    """
    Generate code fragment for constructor arguments
    :param property_meta: list of arguments to pass to method
    :return: formatted string of joined arguments,  or empty string if none
    """

    # add **kwargs to parameters, to allow for "Extra parameters" in call to constructor
    args = {p: m['type'] for p, m in property_meta.items()}
    args['**kwargs'] = 'Optional[Any]'
    params = [f'{p}: {t}' for p, t in args.items()]

    if len(args) > 3:
        # if the args don't fit on 1 line, we break them over multiple lines with 17 spaces of indentation
        # so the line up nicely in the constructor
        args_string = ',\n' + \
            indent_lines(',\n'.join(params), level=17, spaces=1)
    else:
        args_string = ', ' + ', '.join(params)

    return args_string


def get_super_args_string(property_meta: Dict[str, dict]) -> str:
    """
    generates python code (string) of arguments to call super class with
    :param property_meta:
    :return: str - formatted python code
    """
    super_args_string = ''
    params = [f'{p}={p}' for p in property_meta.keys()]
    # make sure all arguments bubble up
    params.append('**kwargs')
    if len(property_meta) > 0:
        if len(property_meta) > 3:
            # hard to properly indent, as it depends on the strlen of the super class
            # we indent a bit to make it work, and have auto indent fix it properly
            super_args_string = ',\n' + \
                indent_lines(',\n'.join(params), level=17, spaces=1)
        else:
            super_args_string = ', ' + ', '.join(params)
    return super_args_string


def get_call_super_classes_string(super_classes: List[str], property_meta: Dict[str, dict]) -> str:
    """
    Generate code to call all supers
    :param super_classes: list of super classes
    :param property_meta: arguments to call super class with
    :return: formatted string of python code
    """
    call_super_classes: List[str] = []
    for super_class in super_classes:
        # arguments to call super with
        args_string = get_super_args_string(property_meta)
        call_super_classes.append(indent_lines(
            f'{super_class}.__init__(self{args_string})', level=2))
    return '\n'.join(call_super_classes)


def get_class_attributes_description(property_meta: Dict[str, dict]) -> List[str]:
    """
    Generate "attributes" part of class description based on class properties
    :param property_meta:
    :return:
    """
    class_descriptions: List[str] = []
    if len(property_meta) > 0:
        class_descriptions.append('\n    Attributes:')
    for property_name, meta in property_meta.items():
        class_descriptions.append(indent_lines(f'{property_name} ({meta["type"]}):', level=1)
                                  + '\n'
                                  + indent_lines(f'{meta["description"]}', level=3))
    return class_descriptions


def get_class(obj_name: str, obj: Dict[str, Any], all_properties: Dict[str, Any]) -> str:
    """
    Generated documented python code for a class representing the object indicated by obj_name
    :param obj_name: Name of class
    :param obj: list with definition of class, properties, etc
    :param all_properties: List of all properties (through class hierarchy)
    :return:
    """
    parents = [p for p in obj['parents']]
    # add internal super class to "root" class (no parents)
    if len(parents) == 0:
        parents.append('SchemaEntity')

    # keep track of super classes to call
    super_classes: List[str] = [p for p in parents]

    # make sure all Abstract classes are actually abstract
    if re.match('^Abstract', obj_name):
        parents.append('ABC')

    property_meta: Dict[str, Dict[str, str]] = {}
    instance_type = f"_type = '{obj_name}'"
    for property_name, property_description in all_properties.items():
        if property_name == '_type':
            continue

        # create dict with properties and meta info
        # be sure to strip the description strings, as they mess with alignment otherwise
        property_meta[property_name] = {
            'type': get_type(property_description),
            'description': '\n'.join([line.strip() for line in property_description["description"].split('\n')])
        }

    # get object/class description from schema, and clean up some white space
    class_descriptions = [s.strip() for s in obj['description'].split('\n')]
    # add  attribute descriptions to class description
    class_descriptions.extend(get_class_attributes_description(property_meta))

    # constructor arguments
    args_string = get_args_string(property_meta)
    constructor_description = get_constructor_description(property_meta)

    call_super_classes = get_call_super_classes_string(
        super_classes, property_meta)

    constructor = (
        f'def __init__(self{args_string}):\n'
        f'{constructor_description}\n'
        f'{call_super_classes}'
    )

    parent_string = ''
    if len(parents) > 0:
        parent_string = f'({", ".join(parents)})'
    class_description = indent_lines('\n'.join(class_descriptions), level=1)

    return(
        f'class {obj_name}{parent_string}:\n'
        '    """\n'
        f'    {class_description}\n'
        '    """\n'
        f'    {instance_type}\n\n'
        f'    {constructor}\n\n'
    )


def get_classes(objects: Dict[str, dict]) -> List[str]:
    """
    Generates python source code for classes based on the list (Dict) of objects provided
    :param objects: Dict
    """

    parent_list = get_parent_list(objects)

    classes: List[str] = []
    for obj_name, obj in objects.items():
        hierarchy = [obj_name, *parent_list[obj_name]]
        all_properties = get_all_properties(hierarchy, objects=objects)
        classes.append(get_class(obj_name=obj_name, obj=obj,
                       all_properties=all_properties))
    classes.append('\n')
    return classes


def main():
    # get schema
    event_schema = get_collector_config().event_schema

    with open('schema.py', 'w') as output:
        # some imports
        imports = [
            'from typing import List, Dict, Any, Optional',
            'from abc import ABC',
            'from objectiv_backend.schema.schema_utils import SchemaEntity'
        ]
        output.write('\n'.join(imports) + '\n\n\n')
        # process contexts (needed for events, so we do these first)
        output.write('\n'.join(get_classes(event_schema.contexts.schema)))
        # process events
        output.write('\n'.join(get_classes(event_schema.events.schema)))

        output.write('\n'.join(get_context_factory(
            event_schema.contexts.schema)) + '\n\n')
        output.write('\n'.join(get_event_factory(
            event_schema.events.schema)) + '\n\n\n')
        output.write(get_event_maker())


if __name__ == '__main__':
    main()
