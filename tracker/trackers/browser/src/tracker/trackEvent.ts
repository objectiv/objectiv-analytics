import { AbstractEvent, AbstractGlobalContext, AbstractLocationContext } from '@objectiv/schema';
import ExtendableError from 'es6-error';
import { AnyLocationContext, BrowserTracker, TaggableElement } from '../';
import { getTracker } from '../global/getTracker';
import { parseLocationContext } from '../structs';
import { TaggingAttribute } from '../TaggingAttribute';
import { trackerErrorHandler, TrackOnErrorCallback } from '../trackerErrorHandler';
import { isTaggableElement } from '../typeGuards';
import { findTaggedParentElements } from './findTaggedParentElements';

/**
 * All of our EventFactories have the same signature
 */
type EventFactory = (props?: {
  location_stack?: AbstractLocationContext[];
  global_contexts?: AbstractGlobalContext[];
}) => Omit<AbstractEvent, 'id' | 'time'>;

/**
 * The parameters of `trackEvent`
 */
export type TrackEventParameters = {
  eventFactory: EventFactory;
  element: TaggableElement | EventTarget;
  tracker?: BrowserTracker;
  trackerId?: string;
  onError?: TrackOnErrorCallback;
};

/**
 * A custom error thrown by trackEvent calls.
 */
export class TrackEventError extends ExtendableError {}

/**
 * 1. Traverses the DOM to reconstruct the component stack
 * 2. Uses the elements stack, inferred either via DOM or parent attributes, to reconstruct a LocationStack
 * 3. Factors a new event with the given eventFactory
 * 4. Tracks the new Event via WebTracker
 */
export const trackEvent = (parameters: TrackEventParameters) => {
  try {
    const { eventFactory, element, tracker = getTracker(parameters.trackerId) } = parameters;

    // For trackable Elements traverse the DOM to reconstruct their Location
    const locationStack: AnyLocationContext[] = [];
    if (isTaggableElement(element)) {
      // Retrieve parent Tracked Elements
      const elementsStack = findTaggedParentElements(element).reverse();

      // Re-hydrate Location Stack
      elementsStack.forEach((element) => {
        // Get, parse, validate, hydrate and push Location Context in the Location Stack
        locationStack.push(parseLocationContext(element.getAttribute(TaggingAttribute.context)));
      });
    }

    // Create new Event
    const newEvent = eventFactory({ location_stack: locationStack });

    // Track
    tracker.trackEvent(newEvent);
  } catch (error) {
    trackerErrorHandler(error, parameters, parameters.onError);
  }
};
