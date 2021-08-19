import { findTrackedElementsInDOM } from './findTrackedElementsInDOM';
import { isTrackedElement } from './isTrackedElement';
import { TrackingAttribute } from './TrackingAttributes';

/**
 * Our Click Event listener will traverse the DOM and reconstruct a LocationStack, then use WebTracker to transport it.
 */
export const clickEventListener = (event: Event, element: HTMLElement) => {
  if (!isTrackedElement(event.target)) {
    return;
  }

  const targetElementId = event.target.getAttribute(TrackingAttribute.objectivElementId);
  const elementId = element.getAttribute(TrackingAttribute.objectivElementId);
  if (targetElementId !== elementId) {
    return;
  }

  const trackedElements = findTrackedElementsInDOM(element).reverse();

  // TODO actual tracking implementation using core api

  console.log(element.dataset, trackedElements);
};
