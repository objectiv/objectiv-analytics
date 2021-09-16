// noinspection UnnecessaryLocalVariableJS

/**
 *
 * Script to generate Typescript definitions of events and contexts used by the tracker, based on the centralized
 * schema. The schema directory itself can be found in the root of the git repository (/schema). The base schema is in
 * /schema/base_schema.json5.
 * Additionally, the script will look for extensions there, and will add them to the generated classes and interfaces.
 *
 * Usage is pretty straight forward:
 *    ```node generate.js```
 * That's all there is to it.
 *
 */

const fs = require('fs');
const JSON5 = require('json5');

const DISCRIMINATING_PROPERTY_PREFIX = '_';

// TODO: naming of these should come from the schema
const EVENT_DISCRIMINATOR = '_type';
const CONTEXT_DISCRIMINATOR = '_type';

// where to find the base schema files, by default we look in the root of the repository
const schema_dir = '../../../../schema/';

// where to find the core schema package files
const core_schema_package_dir = '../../../core/schema/src/';

// where to find the core tracker package source files
const core_tracker_package_dir = '../../../core/tracker/src/';

// name of base schema, will be loaded first
const base_schema_file = 'base_schema.json5';

// contains object, describing the object, eg, stuff like:
// class_name, properties, parent, abstract, type, interfaces
const object_definitions = {};

// contains actual typescript declarations of object
const object_declarations = {
  abstracts: {},
  events: {},
  global_contexts: {},
  location_contexts: {},
};

// contains factories to create instances of events / contexts
const object_factories = {
  EventFactories: {},
  ContextFactories: {},
};

// list to cache list of abstract parents of interfaces
const toParent = {};
function getParents(class_name) {
  if (toParent[class_name]) {
    return [...getParents(toParent[class_name]), ...[toParent[class_name]]];
  } else {
    return [];
  }
}

function getDefinition(class_name) {
  if (object_definitions[class_name]) {
    return object_definitions[class_name];
  }
  return false;
}

function camelToUnderscore(key) {
  const result = key.replace(/([A-Z])/g, ' $1');
  return result.split(' ').join('_').toLowerCase();
}

// Here we create the actual ts definition, based on a very simple template
function createDefinition(
  params = {
    class_name: '',
    properties: [],
    abstract: false,
    parent: false,
    definition_type: 'class',
    description: '',
  }
) {
  const p_list = [];
  Object.keys(params.properties).forEach((property) => {
    // add description for property
    if (params.properties[property]['description']) {
      p_list.push(`/**\n * ${params.properties[property]['description'].split('\n').join('\n *')}\n */`);
    }
    if (params.properties[property]['type']) {
      p_list.push(`${property}: ${get_property_definition(params.properties[property])};\n`);
    } else if (params.properties[property]['discriminator']) {
      p_list.push(`readonly ${property} = ${params.properties[property]['discriminator']};\n`);
    } else {
      p_list.push(`readonly ${property}: ${params.properties[property]['value']};\n`);
    }
  });

  let description = '';
  if ('description' in params && params.description !== undefined && params.description !== '') {
    description = params.description.split('\n').join('\n * ');
  }

  const parents = getParents(params.class_name);
  parents.push(params.class_name);
  const inheritance = parents.reverse().join(' -> ');
  const tpl =
    `/**\n` +
    ` * ${description}\n` +
    ` * Inheritance: ${inheritance}\n` +
    ` */\n` +
    `export ${params.abstract ? 'abstract ' : ''}${params.definition_type} ${params.class_name}` +
    `${params.parent ? ' extends ' + params.parent : ''}` +
    ` {\n` +
    `\t${p_list.join('\n\t')}\n` +
    `}`;
  return tpl;
}

// creates factory methods, based on the interfaces generated.
function createFactory(
  params = {
    class_name: '',
    properties: [],
    abstract: false,
    parent: false,
    definition_type: 'class',
    description: '',
  }
) {
  // we set the literal discriminators first, so they won't be overridden
  // by parent classes.
  const object_discriminator = {};
  if (params.object_type === 'context') {
    object_discriminator[CONTEXT_DISCRIMINATOR] = { value: `'${params.class_name}'` };
  } else {
    object_discriminator[EVENT_DISCRIMINATOR] = { value: `'${params.class_name}'` };
  }

  // we resolve all the properties, based on the ancestry of this class
  // first, compose / merge properties from all parents
  const merged_properties_temp = [object_discriminator];

  // add properties in order of hierarchy
  getParents(params.class_name).forEach((parent) => {
    const parent_params = getDefinition(parent);
    merged_properties_temp.push(parent_params.properties);
  });

  // finally add this objects properties
  merged_properties_temp.push(params.properties);

  // now we merge all of the defined properties, hierarchically (from parent to child)
  // taking care not to overwrite existing ones
  const merged_properties = {};
  merged_properties_temp.forEach((mpt) => {
    Object.keys(mpt).forEach((property) => {
      if (!(property in merged_properties)) {
        merged_properties[property] = mpt[property];
      }
    });
  });

  const discriminators = [];
  const properties = [];
  const props = {};
  const props_name = 'props';

  // factories for the events have some properties that need to be treated differently
  // - location_stack and global_contexts are always optional because most often the Tracker provides them
  // - id is not overridable because the Tracker is responsible to provide one
  // - time is not overridable because the Tracker is responsible to provide one
  let are_all_props_optional = true;
  const return_omit = [];
  Object.keys(merged_properties).forEach((mp) => {
    if (merged_properties[mp]['discriminator']) {
      discriminators.push(`${mp}: true`);
    } else if (merged_properties[mp]['type']) {
      if (params.object_type === 'event' && ['location_stack', 'global_contexts'].includes(mp)) {
        // because the global_contexts and location_stack arrays are optional
        // we provide an empty array as default here
        properties.push(`${mp}: ${props_name}?.${mp} ?? []`);
        props[mp] = `${mp}?: ${merged_properties[mp]['type']}`;
      } else if (params.object_type === 'event' && ['id', 'time'].includes(mp)) {
        // simply don't add the property and adjust the return type to omit it as well
        return_omit.push(mp);
      } else {
        are_all_props_optional = false;
        properties.push(`${mp}: ${props_name}.${mp}`);
        props[mp] = `${mp}: ${merged_properties[mp]['type']}`;
      }
    } else if (merged_properties[mp]['value']) {
      properties.push(`${mp}: ${merged_properties[mp]['value']}`);
    }
  });

  const class_name = params.class_name;

  // we have a special return type, that allows to omit certain properties, which will be
  // populated at a later stage
  const return_type = return_omit.length > 0 ? `Omit<${class_name}, '${return_omit.join("' | '")}'>` : class_name;

  // generate function params, and combine with their description from the base schema
  // the form is something like:
  //  @param {param_type} props.param - param_description
  const f_params = [`@param {Object} ${props_name} - factory properties`];
  Object.keys(props).forEach((key) => {
    const property = merged_properties[key];
    f_params.push(
      `@param {${property.type}} ${props_name}.${key} - ${property.description.split('\n').join('\n  *         ')}`
    );
  });

  // description of factory function. It combines a description of the class, the parameters and the return type
  const description =
    `/** Creates instance of ${class_name} \n` +
    `  * ${f_params.join('\n  * ')}\n` +
    `  * @returns {${return_type}} - ${class_name}: ${params.description.split('\n').join('\n  * \t')}\n` +
    ` */\n`;

  const tpl =
    `${description}` +
    `export const make${params.class_name} = ( ${props_name}${are_all_props_optional ? '?' : ''}: { ${Object.values(
      props
    ).join('; ')} }): 
    ${return_type} => ({\n` +
    `\t${discriminators.join(',\n\t')},\n` +
    `\t${properties.join(',\n\t')},\n` +
    `});\n`;

  return tpl;
}

// in out class hierarchy, we cannot extend interfaces, so we use abstract classes in the hierarchy in stead. This
// slightly deviates from the original schema hierarchy, and so we add abstract classes in between if need be.
// Additionally, if an abstract class and interface overlap (eg. we create AbstractSessionContext, but SessionContext
// already exists), we make sure to re-insert the existing interface below the newly created class, to preserve the
// original hierarchy as well as we can.
function createMissingAbstracts(
  params = {
    class_name: '',
    properties: {},
    abstract: false,
    parent: false,
    definition_type: 'class',
    description: '',
  }
) {
  // if we have a parent and our parent is not abstract, we cannot extend it
  // so create a new one if needed
  if (params.parent) {
    let class_name = params.parent;
    if (!params.parent.match(/Abstract/)) {
      class_name = `Abstract${params.parent}`;
    }

    // if the abstract hasn't been created yet, let's do it now
    if (!object_definitions[class_name]) {
      const discriminator = camelToUnderscore(class_name.replace('Abstract', ''));
      const properties = {};
      properties[DISCRIMINATING_PROPERTY_PREFIX + discriminator] = {};
      properties[DISCRIMINATING_PROPERTY_PREFIX + discriminator]['discriminator'] = true;

      // let's find the parent
      let parent = getParents(params.class_name).pop();

      /**
       * if our parent isn't abstract, we try to make it so
       * however, if that means we should become our own parent, that's not ok.
       * example:
       * DocumentLoadedEvent -> NonInteractiveEvent -> AbstractEvent
       *
       * in this case, the outcome is
       * DocumentLoadedEvent -> AbstractNonInteractiveEvent   \
       *                                                         -> AbstractEvent
       *                                NonInteractiveEvent   /
       *
       * Which means we have to:
       *  - create the AbstractNoninteractiveEvent
       *  - change the hierarchy
       *
       * So we create a new parent for DocumentLoadedEvent (AbstractNoninteractiveEvent), and attach it
       * to the parent of NonInteractiveEvent (parent of the parent).
       *
       */

      if (!parent.match(/^Abstract/) && 'Abstract' + parent !== class_name) {
        parent = 'Abstract' + parent;
      } else {
        // we need the parent of the parent
        parent = getParents(parent).pop();
      }

      const intermediate_params = {
        class_name: class_name,
        properties: properties,
        abstract: true,
        parent: parent,
        definition_type: 'class',
        description: '',
      };

      // add params to map
      object_definitions[class_name] = intermediate_params;
      // add to parent map
      toParent[class_name] = parent;
      createMissingAbstracts(intermediate_params);
    }
    // update params with new parent class
    params.parent = class_name;
    // update parent map
    toParent[params.class_name] = class_name;
  }
  return params;
}

// parse json-schema like property definition
// so we can use it to generate TS
// returns the type of the property.
function get_property_definition(params = {}) {
  switch (params['type']) {
    case 'array':
      return `${params['items']['type']}[]`;
    case 'str':
      return 'string';
    case 'integer':
      // too bad we don't have ints
      // alternatively, we could use big ints here
      return 'number';
    default:
      return params['type'];
  }
}

const files = fs.readdirSync(schema_dir);

// read all schema files
const all_schema = {};
files.forEach((fn) => {
  if (fn.match(/[a-z0-9_]+\.json5?$/) && !fn.match('event_list.json5')) {
    const data = fs.readFileSync(schema_dir + fn, 'utf-8');
    all_schema[fn] = JSON5.parse(data, (key, value) => {
      // clean up `description` fields from json5 schema
      // we remove excess whitespace padding as a result from indentation in the schema
      // we also remove the final newline
      if (key === 'description') {
        return value.replace(/^\s+/gm, '').replace(/\n$/, '');
      }
      return value;
    });
  } else {
    console.log(`ignoring invalid file: ${fn}`);
  }
});

// start with base schema
const schema = all_schema[base_schema_file];
delete all_schema[base_schema_file];

// now add extensions if any
Object.keys(all_schema).forEach((extension_file) => {
  const extension = all_schema[extension_file];
  console.log(`Loading extension ${extension['name']} from ${extension_file}`);

  // events
  Object.keys(extension['events']).forEach((event_type) => {
    if (!(event_type in schema['events'])) {
      // only add if it doesn't already exist
      schema['events'][event_type] = extension['events'][event_type];
    } else {
      Object.keys(extension['events'][event_type]['properties']).forEach((property) => {
        if (!(property in schema['events'][event_type]['properties'])) {
          schema['events'][event_type]['properties'][property] =
            extension['events'][event_type]['properties'][property];
        } else {
          console.log(`Not overriding existing property '${property}'`);
        }
      });
    }
  });
  // contexts
  Object.keys(extension['contexts']).forEach((context_type) => {
    if (!(context_type in schema['contexts'])) {
      // only add if it doesn't already exist
      schema['contexts'][context_type] = extension['contexts'][context_type];
    } else {
      Object.keys(extension['contexts'][context_type]['properties']).forEach((property) => {
        if (!(property in schema['contexts'][context_type]['properties'])) {
          schema['contexts'][context_type]['properties'][property] =
            extension['contexts'][context_type]['properties'][property];
        } else {
          console.log(`Not overriding existing property '${property}'`);
        }
      });
    }
  });
});

// first do events
const events = schema['events'];
Object.keys(events).forEach((event_type) => {
  // if we have more than 0 parents
  if (events[event_type]['parents'].length > 0) {
    toParent[event_type] = events[event_type]['parents'][0];
  } else {
    toParent[event_type] = '';
  }
});

Object.entries(events).forEach(([event_type, event]) => {
  const properties = {};
  let abstract = false;
  let parent = undefined;
  let definition_type;

  // check if this is an abstract class
  if (event_type.match(/Abstract.*?/)) {
    // top level abstract classes don't need the discriminator
    if (event['parents'].length > 0) {
      const discriminator = camelToUnderscore(event_type.replace('Abstract', ''));
      properties[DISCRIMINATING_PROPERTY_PREFIX + discriminator] = { discriminator: true };
    }
    abstract = true;
    definition_type = 'class';
  } else {
    properties[EVENT_DISCRIMINATOR] = {
      description: 'Typescript discriminator',
      value: `'${event_type}'`,
    };
    definition_type = 'interface';
  }

  if (event['properties']) {
    Object.keys(event['properties']).forEach((property_name) => {
      properties[property_name] = {
        description: event['properties'][property_name]['description'],
        type: get_property_definition(event['properties'][property_name]),
      };
    });
  }

  // check if we extend any parents
  // we take the first one, if it exists
  if (event['parents'].length > 0) {
    parent = event['parents'].shift();
  }

  object_definitions[event_type] = {
    object_type: 'event',
    class_name: event_type,
    properties: properties,
    abstract: abstract,
    parent: parent,
    definition_type: definition_type,
    description: event['description'],
  };
});

const contexts = schema['contexts'];

// first determine parents for non abstract contexts
// so we know which are location contexts
Object.keys(contexts).forEach((context_type) => {
  if (contexts[context_type]['parents'] && contexts[context_type]['parents'].length > 0) {
    toParent[context_type] = contexts[context_type]['parents'][0];
  } else {
    toParent[context_type] = '';
  }
});

Object.entries(contexts).forEach(([context_type, context]) => {
  const properties = {};
  let abstract = false;
  let parent = false;
  let definition_type;
  let stack_type;

  // check if this is an abstract class
  if (context_type.match(/Abstract.*?/)) {
    // top level abstract classes don't need the discriminator
    if (context['parents'] && context['parents'].length > 0) {
      const discriminator = camelToUnderscore(context_type.replace('Abstract', ''));
      properties[DISCRIMINATING_PROPERTY_PREFIX + discriminator] = { discriminator: true };
    }
    abstract = true;
    definition_type = 'class';
    stack_type = 'abstracts';
  } else {
    // check ancestry of context, if this is a location or global context
    const parents = getParents(context_type);
    if (parents.includes('AbstractLocationContext')) {
      stack_type = 'location_contexts';
    } else {
      stack_type = 'global_contexts';
    }

    // literal discriminator for non-abstract class
    properties[CONTEXT_DISCRIMINATOR] = {
      description: 'Typescript discriminator',
      value: `'${context_type}'`,
    };

    definition_type = 'interface';
  }

  if (context['properties']) {
    Object.keys(context['properties']).forEach((property_name) => {
      properties[property_name] = {
        description: context['properties'][property_name]['description'],
        type: get_property_definition(context['properties'][property_name]),
      };
    });
  }

  // check if we extend any parents
  if (context['parents'] && context['parents'].length > 0) {
    parent = context['parents'].shift();
  }

  object_definitions[context_type] = {
    object_type: 'context',
    class_name: context_type,
    properties: properties,
    abstract: abstract,
    parent: parent,
    definition_type: definition_type,
    stack_type: stack_type,
    description: context['description'],
  };
});

// let's fix inheritance properly, objects (interfaces) extending non abstracts are not allowed
// so we add an abstract class on top, that extends the parents' parent (until we find an abstract)
Object.entries(object_definitions).forEach(([object_type, object_definition]) => {
  object_definitions[object_type] = createMissingAbstracts(object_definition);
});

/**
 * a little bit of cleaning / housekeeping. If:
 *  - an object is not abstract
 *  - but there is an abstract version of it
 *  - and it's not its parent
 * we fix that here.
 *
 * example:
 * in OSF:   ItemContext -> SectionContext -> AbstractLocationContext -> AbstractContext
 * In TS this is represented as:
 *     ItemContext     \
 *                         -> AbstractSectionContext -> AbstractLocationContext -> AbstractContext
 *     SectionContext  /
 *
 * Additionally, it moves the properties, as defined in SectionContext to AbstractSectionContext.
 *
 */
Object.entries(object_definitions).forEach(([object_type, object_definition]) => {
  const abstract_class_name = 'Abstract' + object_definition['class_name'];
  if (
    !object_definition.abstract &&
    object_definitions[abstract_class_name] &&
    object_definition['parent'] !== abstract_class_name
  ) {
    // we move it
    object_definitions[object_type]['parent'] = abstract_class_name;
    toParent[object_type] = abstract_class_name;

    // if it defines any properties, we move them to the parent
    Object.keys(object_definitions[object_type]['properties']).forEach((property) => {
      if (property.substring(0) !== '_' && object_definitions[object_type]['properties'][property]['type']) {
        // add to parent
        object_definitions[abstract_class_name]['properties'][property] =
          object_definitions[object_type]['properties'][property];
        // remove here
        delete object_definitions[object_type]['properties'][property];
      }
    });
  }
});

// now let's generate the object declarations
// and put them in the correct location
Object.entries(object_definitions).forEach(([object_type, object_definition]) => {
  let definition_type = 'events';
  if (object_definition.abstract) {
    definition_type = 'abstracts';
  } else {
    let factory_type = 'EventFactories';
    if (object_definition.object_type === 'context') {
      definition_type = object_definition.stack_type;
      factory_type = 'ContextFactories';
    }

    // write some factories
    // we don't want factories for abstracts; dow!
    const factory = createFactory(object_definitions[object_type]);
    object_factories[factory_type][object_type] = factory;
  }
  object_declarations[definition_type][object_type] = createDefinition(object_definitions[object_type]);
});

Object.keys(object_factories).forEach((factory_type) => {
  const factories = {};

  Object.keys(object_factories[factory_type])
    .sort((a, b) => a.localeCompare(b))
    .forEach((factory) => {
      factories[factory] = object_factories[factory_type][factory];
    });

  const imports = Object.keys(factories);
  if (factory_type === 'EventFactories') {
    imports.push('AbstractLocationContext');
    imports.push('AbstractGlobalContext');
  }
  const import_statement = `import { \n\t${imports.join(',\n\t')}\n} from '@objectiv/schema';\n`;

  const filename = `${core_tracker_package_dir}${factory_type}.ts`;
  fs.writeFileSync(filename, [...[import_statement], ...Object.values(factories)].join('\n'));
  console.log(`Written ${Object.values(factories).length} factories to ${filename}`);
});

// now write some files
Object.keys(object_declarations).forEach((definition_type) => {
  const filename = `${core_schema_package_dir}${definition_type}.d.ts`;

  // list of (abstract) classes to import (as they represent the top of the hierarchy)
  const imports = [];

  // we only import abstract classes, so no need to do this when writing the abstract classes
  // this is because they are defines in a separate file
  if (definition_type !== 'abstracts') {
    // add import statement of abstracts in non- abstract files
    // import { AbstractGlobalContext } from './abstracts';
    // NOTE: there may be duplicates in this array, so make sure to fix that later
    Object.keys(object_declarations[definition_type]).forEach((object_type) => {
      if (object_definitions[object_type].parent && object_definitions[object_type].parent.match(/Abstract/)) {
        imports.push(object_definitions[object_type].parent);
      }
    });
  }
  // if we have more than 0 imports, make them unique (cast to set) and generate import statement
  const import_statement =
    imports.length > 0 ? `import {${[...new Set(imports)].join(',')}} from './abstracts';` : null;

  // write imports and declarations to file
  fs.writeFileSync(
    filename,
    [...[import_statement], ...Object.values(object_declarations[definition_type])].join('\n\n')
  );
  console.log(`Written ${Object.values(object_declarations[definition_type]).length} definitions to ${filename}`);
});

// generate index for all declarations
// this includes all generated types, as well as those in static.d.ts
const export_file_list = [...Object.keys(object_declarations), ['static']];
const index_filename = `${core_schema_package_dir}index.d.ts`;
fs.writeFileSync(
  index_filename,
  export_file_list
    .map((element) => {
      return `export * from './${element}';`;
    })
    .join('\n')
);
console.log(`Written ${export_file_list.length} exports to ${index_filename}`);
