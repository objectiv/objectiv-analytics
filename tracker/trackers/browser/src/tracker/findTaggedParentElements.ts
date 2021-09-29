import { TaggingAttribute } from '../TaggingAttribute';
import { isCustomParentTaggedElement, isTaggedElement, TaggableElement } from '../typeGuards';

/**
 * Walk the DOM upwards looking for Tagged Elements. The resulting array can be used to reconstruct a Location Stack.
 */
export const findTaggedParentElements = (
  element: TaggableElement | null,
  parentElements: TaggableElement[] = []
): TaggableElement[] => {
  if (!element) {
    return parentElements;
  }

  if (isTaggedElement(element)) {
    parentElements.push(element);
  }

  let nextElement: TaggableElement | null = element.parentElement;

  // If this element has a Parent Tracked Element Id specified, follow that instead of the DOM parentElement
  if (isCustomParentTaggedElement(element)) {
    const parentElementId = element.getAttribute(TaggingAttribute.parentElementId);
    const parentElement = document.querySelector(`[${TaggingAttribute.elementId}='${parentElementId}']`);
    if (!isTaggedElement(parentElement)) {
      console.error(`findTaggedParentElements: missing or invalid Parent Element '${parentElementId}'`);
      return parentElements;
    }
    nextElement = parentElement;
  }

  return findTaggedParentElements(nextElement, parentElements);
};
