/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { BrowserTracker } from '../BrowserTracker';
import { isTaggedElement } from '../common/guards/isTaggedElement';
import { parseLocationContext } from '../common/parsers/parseLocationContext';
import { parseTrackVisibility } from '../common/parsers/parseTrackVisibility';
import { trackerErrorHandler } from '../common/trackerErrorHandler';
import { GuardableElement } from '../definitions/GuardableElement';
import { TaggingAttribute } from '../definitions/TaggingAttribute';
import { trackHiddenEvent } from '../eventTrackers/trackHiddenEvent';

/**
 * Given a removed GuardableElement node it will:
 *
 *   1. Determine whether to track a visibility:hidden event for it.
 *      Hidden Events are triggered only for automatically tracked Elements.
 *
 *   2. Remove the Element from the TrackerElementLocations state.
 *      This is both a clean-up and a way to allow it to be re-rendered as-is, as it happens with some UI libraries.
 */
export const trackRemovedElement = (element: GuardableElement, tracker: BrowserTracker) => {
  try {
    if (isTaggedElement(element)) {
      // Process visibility:hidden events in mode:auto
      if (element.hasAttribute(TaggingAttribute.trackVisibility)) {
        const trackVisibility = parseTrackVisibility(element.getAttribute(TaggingAttribute.trackVisibility));
        if (trackVisibility && trackVisibility.mode === 'auto') {
          trackHiddenEvent({ element, tracker });
        }
      }

      // Remove this element from TrackerState - this will allow it to re-render
      if (globalThis.objectiv.devTools) {
        globalThis.objectiv.devTools.LocationTree.remove(
          parseLocationContext(element.getAttribute(TaggingAttribute.context))
        );
      }
    }
  } catch (error) {
    trackerErrorHandler(error);
  }
};
