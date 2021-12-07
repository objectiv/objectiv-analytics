/*
 * Copyright 2021 Objectiv B.V.
 */

import { makeSectionHiddenEvent, makeSectionVisibleEvent } from '@objectiv/tracker-core';
import { InteractiveEventTrackerParameters } from '../definitions/InteractiveEventTrackerParameters';
import { trackEvent } from './trackEvent';

/**
 * trackVisibility is a shorthand for trackEvent. It eases triggering visibility events programmatically
 */
export const trackVisibility = ({
  element,
  locationStack,
  globalContexts,
  tracker,
  isVisible,
  onError,
}: InteractiveEventTrackerParameters & { isVisible: boolean }) => {
  return trackEvent({
    event: isVisible
      ? makeSectionVisibleEvent({ location_stack: locationStack, global_contexts: globalContexts })
      : makeSectionHiddenEvent({ location_stack: locationStack, global_contexts: globalContexts }),
    element,
    tracker,
    onError,
  });
};
