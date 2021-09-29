import { TaggingAttribute } from '../TaggingAttribute';
import { trackerErrorHandler } from '../tracker/trackerErrorHandler';
import { isTaggedElement, TaggedElement } from '../typeGuards';

/**
 * Checks if the given origin TaggedElement and the Event Target are the same Element.
 * TODO: make this behavior configurable per event type
 */
export const isBubbledEvent = (originElement: TaggedElement, eventTarget: EventTarget | null): boolean => {
  try {
    // Let Events originating from non Tracked Elements bubble up to, possibly, a parent Tracked Element
    if (!isTaggedElement(eventTarget)) {
      return false;
    }

    const originElementId = originElement.getAttribute(TaggingAttribute.elementId);
    const targetElementId = eventTarget.getAttribute(TaggingAttribute.elementId);

    return originElementId !== targetElementId;
  } catch (error) {
    trackerErrorHandler(error);
  }
  return false;
};
