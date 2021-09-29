import { TaggingAttribute } from '../TaggingAttribute';
import { BrowserTracker } from '../tracker/BrowserTracker';
import { trackerErrorHandler } from '../tracker/trackerErrorHandler';
import { trackRemovedElement } from './trackRemovedElement';

/**
 * Given a Mutation Observer node containing removed nodes it will determine whether to track visibility:hidden events
 * Hidden Events are triggered only for automatically tracked Elements.
 */
export const trackRemovedElements = (element: Element, tracker: BrowserTracker) => {
  try {
    const elements = element.querySelectorAll(`[${TaggingAttribute.trackVisibility}]`);
    [element, ...Array.from(elements)].forEach((element) => trackRemovedElement(element, tracker));
  } catch (error) {
    trackerErrorHandler(error);
  }
};
