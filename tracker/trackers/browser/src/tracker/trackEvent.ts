import { AbstractEvent, AbstractGlobalContext, AbstractLocationContext } from '@objectiv/schema';
import ExtendableError from 'es6-error';
import { AnyLocationContext, BrowserTracker } from '../';
import { parseLocationContext } from '../structs';
import { TrackingAttribute } from '../TrackingAttributes';
import { isTrackableElement } from '../typeGuards';
import findTrackedParentElements from './findTrackedParentElements';
import { trackerErrorHandler, TrackOnErrorCallback } from './trackerErrorHandler';

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
  element: HTMLElement | SVGElement | EventTarget;
  tracker?: BrowserTracker;
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
    const { eventFactory, element, tracker = window.objectiv.tracker } = parameters;

    // For trackable Elements traverse the DOM to reconstruct their Location
    const locationStack: AnyLocationContext[] = [];
    if (isTrackableElement(element)) {
      // Retrieve parent Tracked Elements
      const elementsStack = findTrackedParentElements(element).reverse();

      // Re-hydrate Location Stack
      elementsStack.forEach((element) => {
        // Get, parse, validate, hydrate and push Location Context in the Location Stack
        locationStack.push(parseLocationContext(element.getAttribute(TrackingAttribute.context)));
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
