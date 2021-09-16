import { makeSectionContext } from '@objectiv/tracker-core';
import { stringifyLocationContext, TrackedElement, TrackingAttribute } from '../../src';

const makeTrackedElement = (
  id: string,
  contextId: string | null,
  tagName: keyof HTMLElementTagNameMap
): TrackedElement => {
  const trackedDiv = document.createElement(tagName);
  trackedDiv.setAttribute(TrackingAttribute.elementId, id);
  if (contextId) {
    trackedDiv.setAttribute(TrackingAttribute.context, stringifyLocationContext(makeSectionContext({ id: contextId })));
  }

  return trackedDiv as TrackedElement;
};

export default makeTrackedElement;
