import { assert, Infer, optional, validate } from 'superstruct';
import {
  StringifiedChildrenTrackingAttributes,
  stringifyChildrenAttribute,
  TrackChildrenParameters,
  TrackChildrenQuery,
} from '../structs';
import { TrackingAttribute } from '../TrackingAttributes';
import { trackerErrorHandler, TrackOnErrorCallback } from './trackerErrorHandler';

/**
 * Used to decorate a Trackable Element with our Children Tracking Attributes.
 *
 * Returns an object containing the children tracking attribute only.
 * This attribute is a serialized list of TrackChildrenQuery objects and will be parsed and executed by our Observer
 * as soon as the elements gets rendered.
 *
 * Examples
 *
 *    trackChildren([
 *      {
 *        queryAll: 'button[aria-label="Previous"]',
 *        trackAs: trackButton({ id: 'prev', text: 'Previous' })
 *      },
 *      {
 *        queryAll: 'button[aria-label="Next"]',
 *        trackAs: trackButton({ id: 'next', text: 'Next' })
 *      }
 *    ])
 */
export const TrackChildrenReturnValue = optional(StringifiedChildrenTrackingAttributes);
export type TrackChildrenReturnValue = Infer<typeof TrackChildrenReturnValue>;

export const trackChildren = (
  parameters: TrackChildrenParameters,
  onError?: TrackOnErrorCallback
): TrackChildrenReturnValue => {
  try {
    // Validate input
    assert(parameters, TrackChildrenParameters);

    // Create output attributes object
    const trackingAttributes = {
      [TrackingAttribute.trackChildren]: stringifyChildrenAttribute(parameters),
    };

    // Validate
    validate(trackingAttributes, StringifiedChildrenTrackingAttributes);

    // Return
    return trackingAttributes;
  } catch (error) {
    return trackerErrorHandler(error, parameters, onError);
  }
};

/**
 * Syntactic sugar to track only one child.
 *
 * Examples
 *
 *    trackChild({
 *      query: '#button1',
 *      trackAs: trackButton({ id: 'button1', text: 'Button 1' })
 *    })
 *
 *    trackChild({
 *      query: '#button2',
 *      trackAs: trackButton({ id: 'button2', text: 'Button 2' })
 *    })
 *
 */
export const trackChild = (parameters: TrackChildrenQuery, onError?: TrackOnErrorCallback) => {
  return trackChildren([parameters], onError);
};
