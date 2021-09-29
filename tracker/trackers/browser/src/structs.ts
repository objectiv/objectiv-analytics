import {
  array,
  assert,
  boolean,
  coerce,
  create,
  define,
  Infer,
  literal,
  object,
  optional,
  string,
  Struct,
  union,
} from 'superstruct';
import { validate as validateUuid } from 'uuid';
import { AnyLocationContext } from './Contexts';
import { TaggingAttribute } from './TaggingAttribute';

/**
 * A custom Struct describing v4 UUIDs
 */
export const Uuid = define<string>('Uuid', (value: any) => validateUuid(value));

/**
 * Generic structs to stringify and parse JSON via create + coerce
 */
export const stringifyStruct = <T = unknown>(object: T, struct: Struct<T>): string => {
  return create(
    object,
    coerce(string(), struct, (value) => JSON.stringify(value))
  );
};

export const parseStruct = <T = unknown>(stringifiedContext: string | null, struct: Struct<T>): T => {
  return create(
    stringifiedContext,
    coerce(struct, string(), (value) => JSON.parse(value))
  );
};

/**
 * Stringifier and Parser for Location Contexts
 */
export const stringifyLocationContext = (contextObject: AnyLocationContext) => {
  return stringifyStruct(contextObject, AnyLocationContext);
};

export const parseLocationContext = (stringifiedContext: string | null) => {
  return parseStruct(stringifiedContext, AnyLocationContext);
};

/**
 * Custom Structs describing stringified booleans + their Stringifier and Parser
 */
export const StringBoolean = union([literal('true'), literal('false')]);

export const stringifyBoolean = (value: boolean) => {
  return create(JSON.stringify(value), StringBoolean);
};

export const parseBoolean = (stringifiedBoolean: string | null) => {
  if (stringifiedBoolean === null) {
    throw new Error('Received `null` while attempting to parse boolean');
  }
  return create(JSON.parse(stringifiedBoolean), boolean());
};

/**
 * Custom Structs for the Visibility Tagging Attribute + their Stringifier and Parser
 */
export const TaggingAttributeVisibilityAuto = object({ mode: literal('auto') });
export type TaggingAttributeVisibilityAuto = Infer<typeof TaggingAttributeVisibilityAuto>;
export const TaggingAttributeVisibilityManual = object({ mode: literal('manual'), isVisible: boolean() });
export type TaggingAttributeVisibilityManual = Infer<typeof TaggingAttributeVisibilityManual>;
export const TaggingAttributeVisibility = union([TaggingAttributeVisibilityAuto, TaggingAttributeVisibilityManual]);
export type TaggingAttributeVisibility = Infer<typeof TaggingAttributeVisibility>;

export const stringifyVisibilityAttribute = (visibility: TaggingAttributeVisibility) => {
  if (!(typeof visibility === 'object')) {
    throw new Error(`Visibility must be an object, received: ${JSON.stringify(visibility)}`);
  }
  return stringifyStruct(visibility, TaggingAttributeVisibility);
};

export const parseVisibilityAttribute = (stringifiedVisibility: string | null) => {
  return parseStruct(stringifiedVisibility, TaggingAttributeVisibility);
};

/**
 * The object that Location Taggers return
 */
export const TaggingAttributes = object({
  [TaggingAttribute.elementId]: Uuid,
  [TaggingAttribute.parentElementId]: optional(Uuid),
  [TaggingAttribute.context]: AnyLocationContext,
  [TaggingAttribute.trackClicks]: optional(boolean()),
  [TaggingAttribute.trackBlurs]: optional(boolean()),
  [TaggingAttribute.trackVisibility]: optional(TaggingAttributeVisibility),
});
export type TaggingAttributes = Infer<typeof TaggingAttributes>;

/**
 * The object that Location Taggers return, stringified
 */
export const StringifiedTaggingAttributes = object({
  [TaggingAttribute.elementId]: Uuid,
  [TaggingAttribute.parentElementId]: optional(Uuid),
  [TaggingAttribute.context]: string(),
  [TaggingAttribute.trackClicks]: optional(StringBoolean),
  [TaggingAttribute.trackBlurs]: optional(StringBoolean),
  [TaggingAttribute.trackVisibility]: optional(string()),
});
export type StringifiedTaggingAttributes = Infer<typeof StringifiedTaggingAttributes>;

/**
 * The object that `tagChildren` calls return
 */
export const ChildrenTaggingQuery = object({
  queryAll: string(),
  tagAs: optional(StringifiedTaggingAttributes),
});
export const ValidChildrenTaggingQuery = object({
  queryAll: string(),
  tagAs: StringifiedTaggingAttributes,
});
export type ChildrenTaggingQuery = Infer<typeof ChildrenTaggingQuery>;

export const ChildrenTaggingAttributes = object({
  [TaggingAttribute.tagChildren]: array(ChildrenTaggingQuery),
});
export type ChildrenTaggingAttributes = Infer<typeof ChildrenTaggingAttributes>;

export const ChildrenTaggingQueries = array(ChildrenTaggingQuery);
export type ChildrenTaggingQueries = Infer<typeof ChildrenTaggingQueries>;

/**
 * The object that `tagChildren` calls return, stringified
 */
export const StringifiedChildrenTaggingAttributes = object({
  [TaggingAttribute.tagChildren]: string(),
});
export type StringifiedChildrenTaggingAttributes = Infer<typeof StringifiedChildrenTaggingAttributes>;

/**
 * Children Tagging Attribute Stringifier and Parser
 */
export const stringifyChildrenTaggingAttribute = (queries: ChildrenTaggingQueries) => {
  if (!(typeof queries === 'object')) {
    throw new Error(`Visibility must be an object, received: ${JSON.stringify(queries)}`);
  }
  queries.forEach((query) => assert(query, ValidChildrenTaggingQuery));
  return create(JSON.stringify(queries), string());
};

export const parseChildrenTaggingAttribute = (stringifiedChildrenTaggingAttribute: string | null) => {
  if (stringifiedChildrenTaggingAttribute === null) {
    throw new Error('Received `null` while attempting to parse Children Tagging Attribute');
  }

  const queries = create(JSON.parse(stringifiedChildrenTaggingAttribute), ChildrenTaggingQueries);
  return create(queries, array(ValidChildrenTaggingQuery));
};
