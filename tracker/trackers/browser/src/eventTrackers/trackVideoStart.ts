/*
 * Copyright 2021 Objectiv B.V.
 */

import { makeVideoStartEvent } from '@objectiv/tracker-core';
import { InteractiveEventTrackerParameters } from '../definitions/InteractiveEventTrackerParameters';
import { trackEvent } from './trackEvent';

/**
 * trackVideoStart is a shorthand for trackEvent. It eases triggering VideoStart events programmatically
 */
export const trackVideoStart = ({
  element,
  locationStack,
  globalContexts,
  tracker,
  onError,
}: InteractiveEventTrackerParameters) => {
  return trackEvent({
    event: makeVideoStartEvent({ location_stack: locationStack, global_contexts: globalContexts }),
    element,
    tracker,
    onError,
  });
};
