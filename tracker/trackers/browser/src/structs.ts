import {
  array,
  assert,
  boolean,
  coerce,
  create,
  define,
  Infer,
  literal,
  number,
  object,
  optional,
  string,
  Struct,
  union,
} from 'superstruct';
import uuid from 'uuid-random';
import { AnyLocationContext } from './Contexts';
import { TaggingAttribute } from './TaggingAttribute';

/**
 * A custom Struct describing v4 UUIDs
 */
export const Uuid = define<string>('Uuid', (value: any) => uuid.test(value));

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
 * Custom Structs for the trackClicks Tagging Attribute + their Stringifier and Parser
 */
export const WaitUntilTrackedOptions = object({
  intervalMs: optional(number()),
  timeoutMs: optional(number()),
  flushQueue: optional(union([literal(false), literal(true), literal('onTimeout')])),
});
export type WaitUntilTrackedOptions = Infer<typeof WaitUntilTrackedOptions>;

export const TrackClicksAttribute = union([
  boolean(),
  object({
    waitUntilTracked: union([literal(true), WaitUntilTrackedOptions]),
  }),
]);
export type TrackClicksAttribute = Infer<typeof TrackClicksAttribute>;

export const stringifyTrackClicksAttribute = (trackClicksAttribute: TrackClicksAttribute) => {
  return stringifyStruct(trackClicksAttribute, TrackClicksAttribute);
};

/**
 * TrackClicks Options Parser
 */
export const WaitForQueueOptions = union([
  object({
    intervalMs: optional(number()),
    timeoutMs: optional(number()),
  }),
]);
export type WaitForQueueOptions = Infer<typeof WaitForQueueOptions>;

export const FlushQueueOptions = union([literal(false), literal(true), literal('onTimeout')]);
export type FlushQueueOptions = Infer<typeof FlushQueueOptions>;

export const TrackClicksOptions = union([
  literal(undefined),
  object({
    waitForQueue: optional(WaitForQueueOptions),
    flushQueue: optional(FlushQueueOptions),
  }),
]);
export type TrackClicksOptions = Infer<typeof TrackClicksOptions>;

export const parseTrackClicksAttribute = (stringifiedTrackClicksAttribute: string | null): TrackClicksOptions => {
  const parsedTrackClicks = parseStruct(stringifiedTrackClicksAttribute, TrackClicksAttribute);

  // Process `true` and `false` shorthands onto their verbose options counterparts
  if (typeof parsedTrackClicks == 'boolean') {
    return parsedTrackClicks ? {} : undefined;
  }

  // Else it must be already an object, from here on trackClicks.enabled will always be `true`
  let trackClickOptions: TrackClicksOptions = {};
  const { waitUntilTracked } = parsedTrackClicks;

  // Process `waitUntilTracked` shorthands - we only have a `true` shorthands to process, `false` means no option
  if (typeof waitUntilTracked == 'boolean') {
    // An empty object means `waitForQueue` will use default internal values for both `timeoutMs` and `intervalMs`
    trackClickOptions.waitForQueue = {};
    // The default `flushQueue` value is to always flush
    trackClickOptions.flushQueue = true;
  } else {
    // waitUntilTracked must be an object
    const { flushQueue, ...waitForQueue } = waitUntilTracked;
    trackClickOptions.flushQueue = flushQueue !== undefined ? flushQueue : true;
    trackClickOptions.waitForQueue = waitForQueue;
  }

  return trackClickOptions;
};

/**
 * Custom Structs for the trackVisibility Tagging Attribute + their Stringifier and Parser
 */
export const TrackVisibilityAttributeAuto = object({ mode: literal('auto') });
export type TrackVisibilityAttributeAuto = Infer<typeof TrackVisibilityAttributeAuto>;
export const TrackVisibilityAttributeManual = object({ mode: literal('manual'), isVisible: boolean() });
export type TrackVisibilityAttributeManual = Infer<typeof TrackVisibilityAttributeManual>;
export const TrackVisibilityAttribute = union([TrackVisibilityAttributeAuto, TrackVisibilityAttributeManual]);
export type TrackVisibilityAttribute = Infer<typeof TrackVisibilityAttribute>;

export const stringifyTrackVisibilityAttribute = (trackVisibilityAttribute: TrackVisibilityAttribute) => {
  if (!(typeof trackVisibilityAttribute === 'object')) {
    throw new Error(`trackVisibility must be an object, received: ${JSON.stringify(trackVisibilityAttribute)}`);
  }
  return stringifyStruct(trackVisibilityAttribute, TrackVisibilityAttribute);
};

export const parseTrackVisibilityAttribute = (stringifiedTrackVisibilityAttribute: string | null) => {
  return parseStruct(stringifiedTrackVisibilityAttribute, TrackVisibilityAttribute);
};

/**
 * The object that Location Taggers return
 */
export const TaggingAttributes = object({
  [TaggingAttribute.elementId]: Uuid,
  [TaggingAttribute.parentElementId]: optional(Uuid),
  [TaggingAttribute.context]: AnyLocationContext,
  [TaggingAttribute.trackClicks]: optional(TrackClicksAttribute),
  [TaggingAttribute.trackBlurs]: optional(boolean()),
  [TaggingAttribute.trackVisibility]: optional(TrackVisibilityAttribute),
});
export type TaggingAttributes = Infer<typeof TaggingAttributes>;

/**
 * The object that Location Taggers return, stringified
 */
export const StringifiedTaggingAttributes = object({
  [TaggingAttribute.elementId]: Uuid,
  [TaggingAttribute.parentElementId]: optional(Uuid),
  [TaggingAttribute.context]: string(),
  [TaggingAttribute.trackClicks]: optional(string()),
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
