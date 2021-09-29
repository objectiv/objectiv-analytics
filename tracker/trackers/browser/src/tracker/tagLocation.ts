import { getObjectKeys } from '@objectiv/tracker-core';
import { boolean, create, func, Infer, is, object, optional, union, validate } from 'superstruct';
import { v4 } from 'uuid';
import {
  AnyActionContext,
  AnyLocationContext,
  AnySectionContext,
  ExpandableSectionContext,
  InputContext,
} from '../Contexts';
import {
  StringifiedTaggingAttributes,
  stringifyBoolean,
  stringifyLocationContext,
  stringifyVisibilityAttribute,
  TaggingAttributeVisibility,
} from '../structs';
import { TaggingAttribute } from '../TaggingAttribute';
import { trackerErrorHandler, TrackOnErrorCallback } from './trackerErrorHandler';

/**
 * Used to decorate a Taggable Element with our Tagging Attributes.
 *
 * Returns an object containing the Tagging Attributes. It's properties are supposed to be spread on the target HTML
 * Element. This allows us to identify elements uniquely in a Document and to reconstruct their Location.
 *
 * For a higher level api see the tagLocationHelpers module.
 *
 * Examples
 *
 *    tagLocation({ instance: makeElementContext({ id: 'section-id' }) })
 *    tagLocation({ instance: makeElementContext({ id: 'section-id' }), { trackClicks: true } })
 *
 */
export const TagLocationReturnValue = optional(StringifiedTaggingAttributes);
export type TagLocationReturnValue = Infer<typeof TagLocationReturnValue>;

export const TagLocationOptions = object({
  trackClicks: optional(boolean()),
  trackBlurs: optional(boolean()),
  trackVisibility: optional(TaggingAttributeVisibility),
  parent: TagLocationReturnValue,
});
export type TagLocationOptions = Infer<typeof TagLocationOptions>;

export const TagLocationParameters = object({
  instance: AnyLocationContext,
  options: optional(TagLocationOptions),
  onError: optional(func()),
});
export type TagLocationParameters = {
  instance: AnyLocationContext;
  options?: TagLocationOptions;
  onError?: TrackOnErrorCallback;
};

// Custom struct to match all Action Contexts + ExpandableSectionContext
export const AnyClickableContext = union([AnyActionContext, ExpandableSectionContext]);

export const tagLocation = (parameters: TagLocationParameters): TagLocationReturnValue => {
  try {
    // Validate input
    const { instance, options } = create(parameters, TagLocationParameters);

    // Determine Context type
    const isClickable = is(instance, AnyClickableContext);
    const isInput = is(instance, InputContext);
    const isSection = is(instance, AnySectionContext);

    // Process options. Gather default attribute values
    const trackClicks = options?.trackClicks ?? (isClickable ? true : undefined);
    const trackBlurs = options?.trackBlurs ?? (isInput ? true : undefined);
    const trackVisibility = options?.trackVisibility ?? (isSection ? { mode: 'auto' } : undefined);
    const parentElementId = options?.parent ? options.parent[TaggingAttribute.elementId] : undefined;

    // Create output attributes object
    const taggingAttributes = {
      [TaggingAttribute.elementId]: v4(),
      [TaggingAttribute.parentElementId]: parentElementId,
      [TaggingAttribute.context]: stringifyLocationContext(instance),
      [TaggingAttribute.trackClicks]: runIfNotUndefined(stringifyBoolean, trackClicks),
      [TaggingAttribute.trackBlurs]: runIfNotUndefined(stringifyBoolean, trackBlurs),
      [TaggingAttribute.trackVisibility]: runIfNotUndefined(stringifyVisibilityAttribute, trackVisibility),
    };

    // Validate
    validate(taggingAttributes, StringifiedTaggingAttributes);

    // Strip out undefined attributes and return
    getObjectKeys(taggingAttributes).forEach((key) => {
      if (taggingAttributes[key] === undefined) {
        delete taggingAttributes[key];
      }
    });

    return taggingAttributes;
  } catch (error) {
    return trackerErrorHandler(error, parameters, parameters?.onError);
  }
};

/**
 * Small helper to execute the given function call only if the given value is not `undefined`
 */
export const runIfNotUndefined = (functionToRun: Function, value: unknown) => {
  if (typeof value === 'undefined') {
    return undefined;
  }

  return functionToRun(value);
};
