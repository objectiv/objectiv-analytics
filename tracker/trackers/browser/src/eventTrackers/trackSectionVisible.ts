/*
 * Copyright 2021 Objectiv B.V.
 */

import { makeSectionVisibleEvent } from '@objectiv/tracker-core';
import { InteractiveEventTrackerParameters } from '../definitions/InteractiveEventTrackerParameters';
import { trackEvent } from './trackEvent';

/**
 * trackSectionVisible is a shorthand for trackEvent. It eases triggering SectionVisible events programmatically
 */
export const trackSectionVisible = ({
  element,
  locationStack,
  globalContexts,
  tracker,
  onError,
}: InteractiveEventTrackerParameters) => {
  return trackEvent({
    event: makeSectionVisibleEvent({ location_stack: locationStack, global_contexts: globalContexts }),
    element,
    tracker,
    onError,
  });
};
