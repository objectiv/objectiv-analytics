import { trackerErrorHandler } from '../tracker/trackerErrorHandler';
import { TrackingAttribute } from '../TrackingAttributes';
import { isTrackedElement, TrackedElement } from '../typeGuards';

/**
 * Checks if the given origin Tracked Element and the Event Target are the same Tracked Element.
 * TODO: make this behavior configurable per event type
 */
export const isBubbledEvent = (originElement: TrackedElement, eventTarget: EventTarget | null): boolean => {
  try {
    // Let Events originating from non Tracked Elements bubble up to, possibly, a parent Tracked Element
    if (!isTrackedElement(eventTarget)) {
      return false;
    }

    const originElementId = originElement.getAttribute(TrackingAttribute.elementId);
    const targetElementId = eventTarget.getAttribute(TrackingAttribute.elementId);

    return originElementId !== targetElementId;
  } catch (error) {
    trackerErrorHandler(error);
  }
  return false;
};

export default isBubbledEvent;
