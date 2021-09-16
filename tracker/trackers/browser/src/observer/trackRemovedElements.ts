import { BrowserTracker } from '../tracker/BrowserTracker';
import { trackerErrorHandler } from '../tracker/trackerErrorHandler';
import { TrackingAttribute } from '../TrackingAttributes';
import trackRemovedElement from './trackRemovedElement';

/**
 * Given a Mutation Observer node containing removed nodes it will determine whether to track visibility:hidden events
 * Hidden Events are triggered only for automatically tracked Elements.
 */
const trackRemovedElements = (element: Element, tracker: BrowserTracker) => {
  try {
    const elements = element.querySelectorAll(`[${TrackingAttribute.trackVisibility}]`);
    [element, ...Array.from(elements)].forEach((element) => trackRemovedElement(element, tracker));
  } catch (error) {
    trackerErrorHandler(error);
  }
};

export default trackRemovedElements;
