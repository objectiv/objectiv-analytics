/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { TaggableElement } from '../definitions/TaggableElement';
import { TaggedElement } from '../definitions/TaggedElement';
import { TaggingAttribute } from '../definitions/TaggingAttribute';
import { isParentTaggedElement } from './guards/isParentTaggedElement';
import { isTaggedElement } from './guards/isTaggedElement';

/**
 * Walk the DOM upwards looking for Tagged Elements. The resulting array can be used to reconstruct a Location Stack.
 */
export const findParentTaggedElements = (
  element: TaggableElement | null,
  parentElements: TaggedElement[] = []
): TaggedElement[] => {
  if (!element) {
    return parentElements;
  }

  if (isTaggedElement(element)) {
    parentElements.push(element);
  }

  let nextElement: TaggableElement | null = element.parentElement;

  // If this element has a Parent Tagged Element specified, follow that instead of the DOM parentElement
  if (isParentTaggedElement(element)) {
    const parentElementId = element.getAttribute(TaggingAttribute.parentElementId);
    const parentElement = document.querySelector(`[${TaggingAttribute.elementId}='${parentElementId}']`);
    if (!isTaggedElement(parentElement)) {
      globalThis.objectiv.devTools?.TrackerConsole.error(
        `findParentTaggedElements: missing or invalid Parent Element '${parentElementId}'`
      );
      return parentElements;
    }
    nextElement = parentElement;
  }

  return findParentTaggedElements(nextElement, parentElements);
};
