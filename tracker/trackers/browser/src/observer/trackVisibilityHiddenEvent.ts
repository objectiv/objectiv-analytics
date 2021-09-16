import { parseVisibilityAttribute } from '../structs';
import { BrowserTracker } from '../tracker/BrowserTracker';
import { trackerErrorHandler } from '../tracker/trackerErrorHandler';
import { trackSectionHidden } from '../tracker/trackEventHelpers';
import { TrackingAttribute } from '../TrackingAttributes';
import { TrackedElement } from '../typeGuards';

/**
 * Checks if the given Node is a tracked element and if we need to trigger a visibility: hidden event for it.
 */
const trackVisibilityHiddenEvent = (element: TrackedElement, tracker: BrowserTracker) => {
  try {
    if (!element.hasAttribute(TrackingAttribute.trackVisibility)) {
      return;
    }
    const trackVisibility = parseVisibilityAttribute(element.getAttribute(TrackingAttribute.trackVisibility));
    if (trackVisibility.mode === 'manual' && !trackVisibility.isVisible) {
      trackSectionHidden({ element, tracker });
    }
  } catch (error) {
    trackerErrorHandler(error);
  }
};

export default trackVisibilityHiddenEvent;
