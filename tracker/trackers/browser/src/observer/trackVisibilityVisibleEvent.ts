import { parseVisibilityAttribute } from '../structs';
import { BrowserTracker } from '../tracker/BrowserTracker';
import { trackerErrorHandler } from '../tracker/trackerErrorHandler';
import { trackSectionVisible } from '../tracker/trackEventHelpers';
import { TrackingAttribute } from '../TrackingAttributes';
import { TrackedElement } from '../typeGuards';

/**
 * Checks if the given Node is a tracked element and if we need to trigger a visibility: visible event for it.
 */
const trackVisibilityVisibleEvent = (element: TrackedElement, tracker: BrowserTracker) => {
  try {
    if (!element.hasAttribute(TrackingAttribute.trackVisibility)) {
      return;
    }
    const trackVisibility = parseVisibilityAttribute(element.getAttribute(TrackingAttribute.trackVisibility));
    if (trackVisibility.mode === 'auto' || (trackVisibility.mode === 'manual' && trackVisibility.isVisible)) {
      trackSectionVisible({ element, tracker });
    }
  } catch (error) {
    trackerErrorHandler(error);
  }
};

export default trackVisibilityVisibleEvent;
