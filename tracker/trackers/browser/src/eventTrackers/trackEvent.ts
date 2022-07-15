/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { LocationStack, TrackerEventAttributes } from '@objectiv/tracker-core';
import { BrowserTracker } from '../BrowserTracker';
import { getElementLocationStack } from '../common/getElementLocationStack';
import { trackerErrorHandler } from '../common/trackerErrorHandler';
import { TrackedElement } from '../definitions/TrackedElement';
import { TrackerErrorHandlerCallback } from '../definitions/TrackerErrorHandlerCallback';
import { getTracker } from '../getTracker';

/**
 * 1. Reconstruct a LocationStack for the given Element by traversing its DOM parents
 * 2. Factors a new Event with the given `_type`
 * 3. Tracks the new Event via WebTracker
 */
export const trackEvent = (parameters: {
  event: TrackerEventAttributes;
  element?: TrackedElement;
  tracker?: BrowserTracker;
  trackerId?: string;
  onError?: TrackerErrorHandlerCallback;
}) => {
  try {
    const { event, element, tracker = getTracker(parameters.trackerId) } = parameters;

    // If the Location Stack of the given Event is empty, and we have an Element, attempt to generate one from the DOM
    let locationStack: LocationStack | undefined = event.location_stack;
    if (locationStack?.length === 0 && element) {
      locationStack = getElementLocationStack({ element });
    }

    // Track
    tracker.trackEvent({ ...event, location_stack: locationStack });
  } catch (error) {
    trackerErrorHandler(error, parameters, parameters.onError);
  }
};
