import { parseVisibilityAttribute } from '../structs';
import { BrowserTracker } from '../tracker/BrowserTracker';
import { trackerErrorHandler } from '../tracker/trackerErrorHandler';
import { trackSectionHidden } from '../tracker/trackEventHelpers';
import { TrackingAttribute } from '../TrackingAttributes';
import { isTrackedElement } from '../typeGuards';

/**
 * Given a removed Element nodes it will determine whether to track a visibility:hidden event for it
 * Hidden Events are triggered only for automatically tracked Elements.
 */
const trackRemovedElements = (element: Element, tracker: BrowserTracker) => {
  try {
    if (isTrackedElement(element)) {
      if (!element.hasAttribute(TrackingAttribute.trackVisibility)) {
        return;
      }
      const trackVisibility = parseVisibilityAttribute(element.getAttribute(TrackingAttribute.trackVisibility));
      if (trackVisibility.mode === 'auto') {
        trackSectionHidden({ element, tracker });
      }
    }
  } catch (error) {
    trackerErrorHandler(error);
  }
};

export default trackRemovedElements;
