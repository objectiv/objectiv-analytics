/*
 * Copyright 2021 Objectiv B.V.
 */

import { makeButtonContext, makeInputContext, makeSectionContext } from '@objectiv/tracker-core';
import { stringifyLocationContext, TaggedElement, TaggingAttribute } from '../../src';

export const makeTaggedElement = (
  id: string,
  contextId: string | null,
  tagName: keyof HTMLElementTagNameMap,
  trackClicks?: boolean,
  trackBlurs?: boolean
): TaggedElement => {
  const trackedDiv = document.createElement(tagName);

  trackedDiv.setAttribute(TaggingAttribute.elementId, id);

  if (contextId && trackClicks) {
    trackedDiv.setAttribute(
      TaggingAttribute.context,
      stringifyLocationContext(makeButtonContext({ id: contextId, text: id }))
    );
  } else if (contextId && trackBlurs) {
    trackedDiv.setAttribute(TaggingAttribute.context, stringifyLocationContext(makeInputContext({ id: contextId })));
  } else if (contextId) {
    trackedDiv.setAttribute(TaggingAttribute.context, stringifyLocationContext(makeSectionContext({ id: contextId })));
  }

  if (trackClicks) {
    trackedDiv.setAttribute(TaggingAttribute.trackClicks, 'true');
  }

  if (trackBlurs) {
    trackedDiv.setAttribute(TaggingAttribute.trackBlurs, 'true');
  }

  return trackedDiv as TaggedElement;
};
