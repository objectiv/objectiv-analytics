import { parseVisibilityAttribute } from '../structs';
import { TaggingAttribute } from '../TaggingAttribute';
import { BrowserTracker } from '../tracker/BrowserTracker';
import { trackerErrorHandler } from '../tracker/trackerErrorHandler';
import { trackSectionHidden } from '../tracker/trackEventHelpers';
import { TaggedElement } from '../typeGuards';

/**
 * Checks if the given Node is a tracked element and if we need to trigger a visibility: hidden event for it.
 */
export const trackVisibilityHiddenEvent = (element: TaggedElement, tracker: BrowserTracker) => {
  try {
    if (!element.hasAttribute(TaggingAttribute.trackVisibility)) {
      return;
    }
    const trackVisibility = parseVisibilityAttribute(element.getAttribute(TaggingAttribute.trackVisibility));
    if (trackVisibility.mode === 'manual' && !trackVisibility.isVisible) {
      trackSectionHidden({ element, tracker });
    }
  } catch (error) {
    trackerErrorHandler(error);
  }
};
