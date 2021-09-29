import { TaggingAttribute } from '../TaggingAttribute';
import { BrowserTracker } from '../tracker/BrowserTracker';
import { trackerErrorHandler } from '../tracker/trackerErrorHandler';
import { processChildrenTaggingElement } from './processChildrenTaggingElement';
import { trackNewElement } from './trackNewElement';

/**
 * Given a Mutation Observer node containing newly added nodes it will track visibility and attach events to them:
 */
export const trackNewElements = (element: Element, tracker: BrowserTracker) => {
  try {
    // Process `tagLocation`, and its helpers, attributes
    const trackedElements = element.querySelectorAll(`[${TaggingAttribute.context}]`);
    [element, ...Array.from(trackedElements)].forEach((element) => trackNewElement(element, tracker));

    // Process `tagChildren` attributes
    const childrenTrackingElements = element.querySelectorAll(`[${TaggingAttribute.tagChildren}]`);
    [element, ...Array.from(childrenTrackingElements)].forEach((element) => {
      processChildrenTaggingElement(element).forEach((queriedElement) => {
        trackNewElement(queriedElement, tracker);
      });
    });
  } catch (error) {
    trackerErrorHandler(error);
  }
};
