/*
 * Copyright 2021 Objectiv B.V.
 */

import { makeApplicationLoadedEvent } from '@objectiv/tracker-core';
import { trackerErrorHandler } from '../common/trackerErrorHandler';
import { NonInteractiveEventTrackerParameters } from '../definitions/NonInteractiveEventTrackerParameters';
import { trackEvent } from './trackEvent';

/**
 * trackApplicationLoaded is a shorthand for trackEvent. It eases triggering ApplicationLoaded events programmatically
 */
export const trackApplicationLoaded = (parameters: NonInteractiveEventTrackerParameters = {}) => {
  try {
    const { element = document, locationStack, globalContexts, tracker } = parameters;
    return trackEvent({
      event: makeApplicationLoadedEvent({ location_stack: locationStack, global_contexts: globalContexts }),
      element,
      tracker,
    });
  } catch (error) {
    trackerErrorHandler(error, parameters, parameters.onError);
  }
};
