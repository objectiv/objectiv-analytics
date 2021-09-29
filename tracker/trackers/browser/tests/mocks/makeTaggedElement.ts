import { makeSectionContext } from '@objectiv/tracker-core';
import { stringifyLocationContext, TaggedElement, TaggingAttribute } from '../../src';

export const makeTaggedElement = (
  id: string,
  contextId: string | null,
  tagName: keyof HTMLElementTagNameMap
): TaggedElement => {
  const trackedDiv = document.createElement(tagName);
  trackedDiv.setAttribute(TaggingAttribute.elementId, id);
  if (contextId) {
    trackedDiv.setAttribute(TaggingAttribute.context, stringifyLocationContext(makeSectionContext({ id: contextId })));
  }

  return trackedDiv as TaggedElement;
};
