/*
 * Copyright 2021 Objectiv B.V.
 */

import { makeVideoPauseEvent } from '@objectiv/tracker-core';
import { InteractiveEventTrackerParameters } from '../definitions/InteractiveEventTrackerParameters';
import { trackEvent } from './trackEvent';

/**
 * trackVideoPause is a shorthand for trackEvent. It eases triggering VideoPause events programmatically
 */
export const trackVideoPause = ({
  element,
  locationStack,
  globalContexts,
  tracker,
  onError,
}: InteractiveEventTrackerParameters) => {
  return trackEvent({
    event: makeVideoPauseEvent({ location_stack: locationStack, global_contexts: globalContexts }),
    element,
    tracker,
    onError,
  });
};
