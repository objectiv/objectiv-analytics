/*
 * Copyright 2021 Objectiv B.V.
 */

import { getLocationPath, TrackerConsole, TrackerElementLocations } from '@objectiv/tracker-core';
import { BrowserTracker } from '../BrowserTracker';
import { getElementLocationStack } from '../common/getElementLocationStack';
import { isTaggedElement } from '../common/guards/isTaggedElement';
import { parseTrackClicks } from '../common/parsers/parseTrackClicks';
import { parseValidate } from '../common/parsers/parseValidate';
import { trackerErrorHandler } from '../common/trackerErrorHandler';
import { TaggingAttribute } from '../definitions/TaggingAttribute';
import { makeBlurEventHandler } from './makeBlurEventHandler';
import { makeClickEventHandler } from './makeClickEventHandler';
import { trackVisibilityVisibleEvent } from './trackVisibilityVisibleEvent';

/**
 * Attaches event handlers to the given Element and triggers visibility Events for it if the Tagging Attributes allow.
 * - All Elements will be checked for visibility tracking and appropriate events will be triggered for them.
 * - Elements with the Objectiv Track Click attribute are bound to EventListener for Buttons, Links.
 * - Elements with the Objectiv Track Blur attribute are bound to EventListener for Inputs.
 * - All processed Elements are decorated with the `tracked` Tagging Attribute so we won't process them again.
 */
export const trackNewElement = (element: Element, tracker: BrowserTracker, console?: TrackerConsole) => {
  try {
    if (isTaggedElement(element)) {
      // Prevent Elements from being tracked multiple times
      if (element.hasAttribute(TaggingAttribute.tracked)) {
        return;
      }
      element.setAttribute(TaggingAttribute.tracked, 'true');

      // Gather Element id and Validate attributes to determine whether we can and if we should validate the Location
      const elementId = element.getAttribute(TaggingAttribute.elementId);
      const validate = parseValidate(element.getAttribute(TaggingAttribute.validate));

      // Add this element to TrackerState - this will also check if its Location is unique
      if (elementId && validate.locationUniqueness) {
        const locationStack = getElementLocationStack({ element, tracker });
        const locationPath = getLocationPath(locationStack);
        const locationAddResult = TrackerElementLocations.add({ elementId, locationPath });

        // If location was not unique, log the issue
        if (console && locationAddResult !== true) {
          const { existingElementId, collidingElementId } = locationAddResult;
          const existingElement = document.querySelector(`[${TaggingAttribute.elementId}='${existingElementId}']`);
          const collidingElement = document.querySelector(`[${TaggingAttribute.elementId}='${collidingElementId}']`);
          console.group(`｢objectiv:trackNewElement｣ Location collision detected: ${locationPath}`);
          console.error(`Existing Element:`, existingElement);
          console.error(`Colliding Element:`, collidingElement);
          console.groupEnd();
        }
      }

      // Visibility: visible tracking
      trackVisibilityVisibleEvent(element, tracker);

      // Click tracking (buttons, links)
      if (element.hasAttribute(TaggingAttribute.trackClicks)) {
        // Parse and validate attribute - then convert it into options
        const trackClicksOptions = parseTrackClicks(element.getAttribute(TaggingAttribute.trackClicks));

        // If trackClicks is specifically disabled, nothing to do
        if (!trackClicksOptions) {
          return;
        }

        // If we don't need to wait for Queue, attach a `passive` event handler - else a `useCapture` one
        if (!trackClicksOptions.waitForQueue) {
          element.addEventListener('click', makeClickEventHandler(element, tracker), { passive: true });
        } else {
          element.addEventListener('click', makeClickEventHandler(element, tracker, trackClicksOptions), true);
        }
      }

      // Blur tracking (inputs)
      if (element.getAttribute(TaggingAttribute.trackBlurs) === 'true') {
        element.addEventListener('blur', makeBlurEventHandler(element, tracker), { passive: true });
      }
    }
  } catch (error) {
    trackerErrorHandler(error);
  }
};
