import { TaggingAttribute } from '../TaggingAttribute';
import { BrowserTracker } from '../tracker/BrowserTracker';
import { trackerErrorHandler } from '../tracker/trackerErrorHandler';
import { isTaggedElement } from '../typeGuards';
import { makeBlurEventListener } from './makeBlurEventListener';
import { makeClickEventListener } from './makeClickEventListener';
import { trackVisibilityVisibleEvent } from './trackVisibilityVisibleEvent';

/**
 * Attaches event handlers to the given Element and triggers visibility Events for it if the Tagging Attributes allow.
 * - All Elements will be checked for visibility tracking and appropriate events will be triggered for them.
 * - Elements with the Objectiv Track Click attribute are bound to EventListener for Buttons, Links.
 * - Elements with the Objectiv Track Blur attribute are bound to EventListener for Inputs.
 */
export const trackNewElement = (element: Element, tracker: BrowserTracker) => {
  try {
    if (isTaggedElement(element)) {
      // Visibility: visible tracking
      trackVisibilityVisibleEvent(element, tracker);

      // Click tracking (buttons, links)
      if (element.getAttribute(TaggingAttribute.trackClicks) === 'true') {
        element.addEventListener('click', makeClickEventListener(element, tracker));
      }

      // Blur tracking (inputs)
      if (element.getAttribute(TaggingAttribute.trackBlurs) === 'true') {
        element.addEventListener('blur', makeBlurEventListener(element, tracker));
      }
    }
  } catch (error) {
    trackerErrorHandler(error);
  }
};
