/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { BrowserTracker } from '../BrowserTracker';
import { findParentTaggedElements } from '../common/findParentTaggedElements';
import { isTaggedElement } from '../common/guards/isTaggedElement';
import { parseLocationContext } from '../common/parsers/parseLocationContext';
import { parseTrackBlurs } from '../common/parsers/parseTrackBlurs';
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
export const trackNewElement = (element: Element, tracker: BrowserTracker) => {
  try {
    if (isTaggedElement(element)) {
      // Prevent Elements from being tracked multiple times
      if (element.hasAttribute(TaggingAttribute.tracked)) {
        return;
      }
      element.setAttribute(TaggingAttribute.tracked, 'true');

      // Gather Element id and Validate attributes to determine whether we can and if we should validate the Location
      const validate = parseValidate(element.getAttribute(TaggingAttribute.validate));

      // Get element Location Context and its id
      const elementLocationContextAttribute = element.getAttribute(TaggingAttribute.context);
      const elementLocationContext = parseLocationContext(elementLocationContextAttribute);

      // Add this element to LocationTree - this will also check if its Location is unique
      if (globalThis.objectiv.devTools && validate.locationUniqueness) {
        let parentLocationContext = null;
        const parent = findParentTaggedElements(element).splice(1).reverse().pop() ?? null;
        if (parent) {
          const parentLocationContextAttribute = parent.getAttribute(TaggingAttribute.context);
          if (parentLocationContextAttribute) {
            parentLocationContext = parseLocationContext(parentLocationContextAttribute);
          }
        }

        globalThis.objectiv.devTools.LocationTree.add(elementLocationContext, parentLocationContext);
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
      if (element.hasAttribute(TaggingAttribute.trackBlurs)) {
        // Parse and validate attribute - then convert it into options
        const trackBlursOptions = parseTrackBlurs(element.getAttribute(TaggingAttribute.trackBlurs));

        // If trackBlurs is specifically disabled, nothing to do
        if (!trackBlursOptions) {
          return;
        }

        element.addEventListener(
          'blur',
          makeBlurEventHandler(element, tracker, trackBlursOptions, elementLocationContext.id),
          { passive: true }
        );
      }
    }
  } catch (error) {
    trackerErrorHandler(error);
  }
};
