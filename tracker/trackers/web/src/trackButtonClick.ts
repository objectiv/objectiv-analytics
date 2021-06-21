import { ButtonContext } from '@objectiv/schema';
import { makeClickEvent } from '@objectiv/tracker-core';
import { WebTracker } from './WebTracker';

/**
 * Event handler to be used for Button-like elements.
 */
export const trackButtonClick = (buttonContext: ButtonContext, tracker: WebTracker) =>
  tracker.trackEvent(makeClickEvent({ location_stack: [buttonContext] }));
