import { parseVisibilityAttribute } from '../structs';
import { TaggingAttribute } from '../TaggingAttribute';
import { BrowserTracker } from '../tracker/BrowserTracker';
import { trackerErrorHandler } from '../tracker/trackerErrorHandler';
import { trackSectionHidden } from '../tracker/trackEventHelpers';
import { isTaggedElement } from '../typeGuards';

/**
 * Given a removed Element nodes it will determine whether to track a visibility:hidden event for it
 * Hidden Events are triggered only for automatically tracked Elements.
 */
export const trackRemovedElement = (element: Element, tracker: BrowserTracker) => {
  try {
    if (isTaggedElement(element)) {
      if (!element.hasAttribute(TaggingAttribute.trackVisibility)) {
        return;
      }
      const trackVisibility = parseVisibilityAttribute(element.getAttribute(TaggingAttribute.trackVisibility));
      if (trackVisibility.mode === 'auto') {
        trackSectionHidden({ element, tracker });
      }
    }
  } catch (error) {
    trackerErrorHandler(error);
  }
};
