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
  StringifiedTrackingAttributes,
  stringifyBoolean,
  stringifyLocationContext,
  stringifyVisibilityAttribute,
  TrackingAttributeVisibility,
} from '../structs';
import { TrackingAttribute } from '../TrackingAttributes';
import { trackerErrorHandler, TrackOnErrorCallback } from './trackerErrorHandler';

/**
 * Used to decorate a Trackable Element with our Tracking Attributes.
 *
 * Returns an object containing the tracking attributes. It's properties are supposed to be spread on the target HTML
 * Element. This allows us to identify elements uniquely in a Document and to reconstruct their Location.
 *
 * For a higher level api see the trackHelpers module.
 *
 * Examples
 *
 *    trackLocation({ instance: makeElementContext({ id: 'section-id' }) })
 *    trackLocation({ instance: makeElementContext({ id: 'section-id' }), { trackClicks: true } })
 *
 */
export const TrackLocationReturnValue = optional(StringifiedTrackingAttributes);
export type TrackLocationReturnValue = Infer<typeof TrackLocationReturnValue>;

export const TrackLocationOptions = object({
  trackClicks: optional(boolean()),
  trackBlurs: optional(boolean()),
  trackVisibility: optional(TrackingAttributeVisibility),
  parentTracker: TrackLocationReturnValue,
});
export type TrackLocationOptions = Infer<typeof TrackLocationOptions>;

export const TrackLocationParameters = object({
  instance: AnyLocationContext,
  options: optional(TrackLocationOptions),
  onError: optional(func()),
});
export type TrackLocationParameters = {
  instance: AnyLocationContext;
  options?: TrackLocationOptions;
  onError?: TrackOnErrorCallback;
};

// Custom struct to match all Action Contexts + ExpandableSectionContext
export const AnyClickableContext = union([AnyActionContext, ExpandableSectionContext]);

export const trackLocation = (parameters: TrackLocationParameters): TrackLocationReturnValue => {
  try {
    // Validate input
    const { instance, options } = create(parameters, TrackLocationParameters);

    // Determine Context type
    const isClickable = is(instance, AnyClickableContext);
    const isInput = is(instance, InputContext);
    const isSection = is(instance, AnySectionContext);

    // Process options. Gather default attribute values
    const trackClicks = options?.trackClicks ?? (isClickable ? true : undefined);
    const trackBlurs = options?.trackBlurs ?? (isInput ? true : undefined);
    const trackVisibility = options?.trackVisibility ?? (isSection ? { mode: 'auto' } : undefined);
    const parentElementId = options?.parentTracker ? options.parentTracker[TrackingAttribute.elementId] : undefined;

    // Create output attributes object
    const trackingAttributes = {
      [TrackingAttribute.elementId]: v4(),
      [TrackingAttribute.parentElementId]: parentElementId,
      [TrackingAttribute.context]: stringifyLocationContext(instance),
      [TrackingAttribute.trackClicks]: runIfNotUndefined(stringifyBoolean, trackClicks),
      [TrackingAttribute.trackBlurs]: runIfNotUndefined(stringifyBoolean, trackBlurs),
      [TrackingAttribute.trackVisibility]: runIfNotUndefined(stringifyVisibilityAttribute, trackVisibility),
    };

    // Validate
    validate(trackingAttributes, StringifiedTrackingAttributes);

    // Strip out undefined attributes and return
    getObjectKeys(trackingAttributes).forEach((key) => {
      if (trackingAttributes[key] === undefined) {
        delete trackingAttributes[key];
      }
    });

    return trackingAttributes;
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
