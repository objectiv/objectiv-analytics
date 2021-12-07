/*
 * Copyright 2021 Objectiv B.V.
 */

import { TrackerConsole } from '@objectiv/tracker-core';
import { BrowserTracker } from '../BrowserTracker';
import { trackerErrorHandler } from '../common/trackerErrorHandler';
import { TaggingAttribute } from '../definitions/TaggingAttribute';
import { processTagChildrenElement } from './processTagChildrenElement';
import { trackNewElement } from './trackNewElement';

/**
 * Given a Mutation Observer node containing newly added nodes it will track visibility and attach events to them:
 */
export const trackNewElements = (element: Element, tracker: BrowserTracker, console?: TrackerConsole) => {
  try {
    // Process `tagLocation`, and its helpers, attributes
    const trackedElements = element.querySelectorAll(`[${TaggingAttribute.context}]`);
    [element, ...Array.from(trackedElements)].forEach((element) => trackNewElement(element, tracker, console));

    // Process `tagChildren` attributes
    const childrenTrackingElements = element.querySelectorAll(`[${TaggingAttribute.tagChildren}]`);
    [element, ...Array.from(childrenTrackingElements)].forEach((element) => {
      processTagChildrenElement(element).forEach((queriedElement) => {
        trackNewElement(queriedElement, tracker, console);
      });
    });
  } catch (error) {
    trackerErrorHandler(error);
  }
};
