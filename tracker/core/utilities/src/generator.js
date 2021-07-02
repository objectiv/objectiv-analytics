// noinspection JSUnfilteredForInLoop,UnnecessaryLocalVariableJS

/**
 *
 * Script to generate Typescript definitions of events and contexts used by the tracker, based on the centralized
 * schema. The schema directory itself can be found in the root of the git repository (/schema). The base schema is in
 * /schema/base_schema.json.
 * Additionally, the script will look for extensions there, and will add them to the generated classes and interfaces.
 *
 * Usage is pretty straight forward:
 *    ```node generate.js```
 * That's all there is to it.
 *
 */

const fs = require('fs');

const DISCRIMINATING_PROPERTY_PREFIX = '_';

// TODO: naming of these should come from the schema
const EVENT_DISCRIMINATOR = 'event';
const CONTEXT_DISCRIMINATOR = '_context_type';

// where to find the base schema files, by default we look in the root of the repository
const schema_dir = '../../../../schema/';

// where to find the core schema package files
const core_schema_package_dir = '../../../core/schema/src/';

// where to find the core tracker package source files
const core_tracker_package_dir = '../../../core/tracker/src/';

// name of base schema, will be loaded first
const base_schema_file = 'base_schema.json';

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
    interfaces: false,
  }
) {
  const p_list = [];
  for (let property in params.properties) {
    const optional = params.properties[property]['optional'] ? '?' : '';
    if (params.properties[property]['type']) {
      p_list.push(`${property}${optional}: ${get_property_definition(params.properties[property])};`);
    } else if (params.properties[property]['discriminator']) {
      p_list.push(`readonly ${property} = ${params.properties[property]['discriminator']};`);
    } else {
      p_list.push(`readonly ${property}${optional}: ${params.properties[property]['value']};`);
    }
  }

  const tpl =
    `export ${params.abstract ? 'abstract ' : ''}${params.definition_type} ${params.class_name}` +
    `${params.parent ? ' extends ' + params.parent : ''}` +
    `${params.interfaces ? ' implements ' + params.interfaces.join(',') : ''}` +
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
    interfaces: false,
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
  const parents = getParents(params.class_name);
  for (let p of parents) {
    let parent_params = getDefinition(p);
    merged_properties_temp.push(parent_params.properties);
  }
  // finally add this objects properties
  merged_properties_temp.push(params.properties);

  // now we merge all of the defined properties, hierarchically (from parent to child)
  const merged_properties = [];
  for (let mpt in merged_properties_temp) {
    for (let property in merged_properties_temp[mpt]) {
      merged_properties[property] = merged_properties_temp[mpt][property];
    }
  }

  const discriminators = [];
  const properties = [];
  const props = [];

  // factories for the events have some optional parameters
  let has_all_optional_properties = true;
  for (let mp in merged_properties) {
    if (merged_properties[mp]['discriminator']) {
      discriminators.push(`${mp}: true`);
    } else if (merged_properties[mp]['type']) {
      if (merged_properties[mp]['optional'] === true) {
        // because the global_contexts and location_stack arrays are optional
        // we provide an empty array as default here
        properties.push(`${mp}: props?.${mp} ?? []`);
        props.push(`${mp}?: ${merged_properties[mp]['type']}`);
      } else {
        has_all_optional_properties = false;
        properties.push(`${mp}: props.${mp}`);
        props.push(`${mp}: ${merged_properties[mp]['type']}`);
      }
    } else if (merged_properties[mp]['value']) {
      properties.push(`${mp}: ${merged_properties[mp]['value']}`);
    }
  }
  const tpl =
    `export const make${params.class_name} = ( props${has_all_optional_properties ? '?' : ''}: { ${props.join(
      '; '
    )} }): ${params.class_name} => ({\n` +
    `\t${discriminators.join(',\n\t')},\n` +
    `\t${properties.join(',\n\t')},\n` +
    `});`;

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
    properties: [],
    abstract: false,
    parent: false,
    definition_type: 'class',
    interfaces: false,
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
      const properties = [];
      properties[DISCRIMINATING_PROPERTY_PREFIX + discriminator] = [];
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
      return `${params['items']}[]`;
    case 'str':
      return 'string';
    case 'integer':
      // too bad we don't have ints
      // alternatively, we could use bigints here
      return 'number';
    default:
      return params['type'];
  }
}

const files = fs.readdirSync(schema_dir);

// read all schema files
const all_schema = {};
for (let fn of files) {
  if (fn.match(/[a-z0-9_]+\.json$/)) {
    let data = fs.readFileSync(schema_dir + fn, 'utf-8');
    all_schema[fn] = JSON.parse(data);
  } else {
    console.log(`ignoring invalid file: ${fn}`);
  }
}

// start with base schema
const schema = all_schema[base_schema_file];
delete all_schema[base_schema_file];

// now add extensions if any
// TODO: allow to add properties to existing contexts
for (let extension_file in all_schema) {
  const extension = all_schema[extension_file];
  console.log(`Loading extension ${extension['name']} from ${extension_file}`);

  // events
  for (let event_type in extension['events']) {
    if (!(event_type in schema['events'])) {
      // only add if it doesn't already exist
      schema['events'][event_type] = extension['events'][event_type];
    }
  }
  // contexts
  for (let context_type in extension['contexts']) {
    if (!(context_type in schema['contexts'])) {
      // only add if it doesn't already exist
      schema['contexts'][context_type] = extension['contexts'][context_type];
    }
  }
}

// first do events
const events = schema['events'];
for (let event_type in events) {
  // if we have more than 0 parents
  if (events[event_type]['parents'].length > 0) {
    toParent[event_type] = events[event_type]['parents'][0];
  } else {
    toParent[event_type] = '';
  }
}

for (let event_type in events) {
  const event = events[event_type];
  const properties = [];
  let abstract = false;
  let parent = undefined;
  let definition_type = undefined;
  let interfaces = false;

  // check if this is an abstract class
  if (event_type.match(/Abstract.*?/)) {
    // top level abstract classes don't need the discriminator
    if (event['parents'].length > 0) {
      const discriminator = camelToUnderscore(event_type.replace('Abstract', ''));
      properties[DISCRIMINATING_PROPERTY_PREFIX + discriminator] = [];
      properties[DISCRIMINATING_PROPERTY_PREFIX + discriminator]['discriminator'] = true;
    }
    abstract = true;
    definition_type = 'class';
  } else {
    properties[EVENT_DISCRIMINATOR] = [];
    properties[EVENT_DISCRIMINATOR]['value'] = `'${event_type}'`;
    definition_type = 'interface';
  }

  if (event['properties']) {
    for (let property_name in event['properties']) {
      properties[property_name] = [];
      properties[property_name]['type'] = get_property_definition(event['properties'][property_name]);
      // some properties may be optional via the `optional` attribute set to true
      if (event['properties'][property_name]['optional'] === true) {
        properties[property_name]['optional'] = true;
      }
    }
  }

  // check if we extend any parents
  // we take the first one, if it exists
  if (event['parents'].length > 0) {
    parent = event['parents'].shift();
  }

  // check for required contexts
  if (event['requiresContext'].length > 0) {
    interfaces = event['requiresContext'];
  }

  object_definitions[event_type] = {
    object_type: 'event',
    class_name: event_type,
    properties: properties,
    abstract: abstract,
    parent: parent,
    definition_type: definition_type,
    // interfaces: interfaces
  };
}

const contexts = schema['contexts'];
// first determine parents for non abstract contexts
// so we know which are location contexts

for (let context_type in contexts) {
  if (contexts[context_type]['parents'] && contexts[context_type]['parents'].length > 0) {
    toParent[context_type] = contexts[context_type]['parents'][0];
  } else {
    toParent[context_type] = '';
  }
}

for (let context_type in contexts) {
  const context = contexts[context_type];
  const properties = [];
  let abstract = false;
  let parent = false;
  let definition_type = undefined;
  // let interfaces = false;
  let stack_type = '';

  // check if this is an abstract class
  if (context_type.match(/Abstract.*?/)) {
    // top level abstract classes don't need the discriminator
    if (context['parents'] && context['parents'].length > 0) {
      const discriminator = camelToUnderscore(context_type.replace('Abstract', ''));
      properties[DISCRIMINATING_PROPERTY_PREFIX + discriminator] = [];
      properties[DISCRIMINATING_PROPERTY_PREFIX + discriminator]['discriminator'] = true;
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
    properties[CONTEXT_DISCRIMINATOR] = [];
    properties[CONTEXT_DISCRIMINATOR]['value'] = `'${context_type}'`;
    definition_type = 'interface';
  }

  if (context['properties']) {
    for (let property_name in context['properties']) {
      properties[property_name] = [];
      properties[property_name]['type'] = get_property_definition(context['properties'][property_name]);
    }
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
    // interfaces: interfaces,
    stack_type: stack_type,
  };
}

// let's fix inheritance properly, objects (interfaces) extending non abstracts are not allowed
// so we add an abstract class on top, that extends the parents' parent (until we find an abstract)
for (let object_type in object_definitions) {
  const object_definition = object_definitions[object_type];
  object_definitions[object_type] = createMissingAbstracts(object_definition);
}

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
for (let object_type in object_definitions) {
  const object_definition = object_definitions[object_type];
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
    for (let property in object_definitions[object_type]['properties']) {
      if (property.substring(0) !== '_' && object_definitions[object_type]['properties'][property]['type']) {
        // add to parent
        object_definitions[abstract_class_name]['properties'][property] =
          object_definitions[object_type]['properties'][property];
        // remove here
        delete object_definitions[object_type]['properties'][property];
      }
    }
  }
}

// now let's generate the object declarations
// and put them in the correct location
for (let object_type in object_definitions) {
  const object_definition = object_definitions[object_type];

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
    let factory = createFactory(object_definitions[object_type]);
    object_factories[factory_type][object_type] = factory;
  }
  object_declarations[definition_type][object_type] = createDefinition(object_definitions[object_type]);
}

for (let factory_type in object_factories) {
  const factories = {};
  for (let factory of Object.keys(object_factories[factory_type]).sort((a, b) => a.localeCompare(b))) {
    factories[factory] = object_factories[factory_type][factory];
  }

  const imports = Object.keys(factories);
  if (factory_type === 'EventFactories') {
    imports.push('AbstractLocationContext');
    imports.push('AbstractGlobalContext');
  }
  const import_statement = `import { \n\t${imports.join(',\n\t')}\n} from '@objectiv/schema';`;

  const filename = `${core_tracker_package_dir}${factory_type}.ts`;
  fs.writeFileSync(filename, [...[import_statement], ...Object.values(factories)].join('\n'));
  console.log(`Written ${Object.values(factories).length} factories to ${filename}`);
}

// now write some files
for (let definition_type in object_declarations) {
  const filename = `${core_schema_package_dir}${definition_type}.d.ts`;

  // list of (abstract) classes to import (as they represent the top of the hierarchy)
  let imports = [];

  // we only import abstract classes, so no need to do this when writing the abstract classes
  // this is because they are defines in a separate file
  if (definition_type !== 'abstracts') {
    // add import statement of abstracts in non- abstract files
    // import { AbstractGlobalContext } from './abstracts';
    // NOTE: there may be duplicates in this array, so make sure to fix that later
    for (let object_type in object_declarations[definition_type]) {
      if (object_definitions[object_type].parent && object_definitions[object_type].parent.match(/Abstract/)) {
        imports.push(object_definitions[object_type].parent);
      }
    }
  }
  // if we have more than 0 imports, make them unique (cast to set) and generate import statement
  const import_statement =
    imports.length > 0 ? `import {${[...new Set(imports)].join(',')}} from './abstracts';` : null;

  // write imports and declarations to file
  fs.writeFileSync(
    filename,
    [...[import_statement], ...Object.values(object_declarations[definition_type])].join('\n')
  );
  console.log(`Written ${Object.values(object_declarations[definition_type]).length} definitions to ${filename}`);
}

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
