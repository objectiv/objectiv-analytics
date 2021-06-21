import { LinkContext } from '@objectiv/schema';
import { makeClickEvent } from '@objectiv/tracker-core';
import { WebTracker } from './WebTracker';

/**
 * Event handler to be used for Link-like elements.
 */
export const trackLinkClick = (linkContext: LinkContext, tracker: WebTracker) =>
  tracker.trackEvent(makeClickEvent({ location_stack: [linkContext] }));
