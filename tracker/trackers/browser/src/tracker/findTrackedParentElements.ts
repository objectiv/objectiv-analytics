import { TrackingAttribute } from '../TrackingAttributes';
import { isCustomParentTrackedElement, isTrackedElement, TrackableElement } from '../typeGuards';

/**
 * Walk the DOM upwards looking for Tracked Elements. The resulting array can be used to reconstruct a Location Stack.
 */
const findTrackedParentElements = (
  element: TrackableElement | null,
  parentElements: TrackableElement[] = []
): TrackableElement[] => {
  if (!element) {
    return parentElements;
  }

  if (isTrackedElement(element)) {
    parentElements.push(element);
  }

  let nextElement: TrackableElement | null = element.parentElement;

  // If this element has a Parent Tracked Element Id specified, follow that instead of the DOM parentElement
  if (isCustomParentTrackedElement(element)) {
    const parentElementId = element.getAttribute(TrackingAttribute.parentElementId);
    const parentElement = document.querySelector(`[${TrackingAttribute.elementId}='${parentElementId}']`);
    if (!isTrackedElement(parentElement)) {
      console.error(`findTrackedParentElements: missing or invalid Parent Element '${parentElementId}'`);
      return parentElements;
    }
    nextElement = parentElement;
  }

  return findTrackedParentElements(nextElement, parentElements);
};

export default findTrackedParentElements;
