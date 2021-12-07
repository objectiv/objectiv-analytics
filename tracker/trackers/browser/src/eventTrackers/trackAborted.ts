/*
 * Copyright 2021 Objectiv B.V.
 */

import { makeAbortedEvent } from '@objectiv/tracker-core';
import { trackerErrorHandler } from '../common/trackerErrorHandler';
import { NonInteractiveEventTrackerParameters } from '../definitions/NonInteractiveEventTrackerParameters';
import { trackEvent } from './trackEvent';

/**
 * trackAborted is a shorthand for trackEvent. It eases triggering Aborted events programmatically
 */
export const trackAborted = (parameters: NonInteractiveEventTrackerParameters = {}) => {
  try {
    const { element = document, locationStack, globalContexts, tracker } = parameters;
    return trackEvent({
      event: makeAbortedEvent({ location_stack: locationStack, global_contexts: globalContexts }),
      element,
      tracker,
    });
  } catch (error) {
    trackerErrorHandler(error, parameters, parameters.onError);
  }
};
