/*
 * Copyright 2021 Objectiv B.V.
 */

import { makeURLChangeEvent } from '@objectiv/tracker-core';
import { trackerErrorHandler } from '../common/trackerErrorHandler';
import { NonInteractiveEventTrackerParameters } from '../definitions/NonInteractiveEventTrackerParameters';
import { trackEvent } from './trackEvent';

/**
 * trackURLChange is a shorthand for trackEvent. It eases triggering URLChange events programmatically
 */
export const trackURLChange = (parameters: NonInteractiveEventTrackerParameters = {}) => {
  try {
    const { element = document, locationStack, globalContexts, tracker } = parameters;
    return trackEvent({
      event: makeURLChangeEvent({ location_stack: locationStack, global_contexts: globalContexts }),
      element,
      tracker,
    });
  } catch (error) {
    trackerErrorHandler(error, parameters, parameters.onError);
  }
};
