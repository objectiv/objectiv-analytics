/*
 * Copyright 2021 Objectiv B.V.
 */

import { makeSectionHiddenEvent } from '@objectiv/tracker-core';
import { InteractiveEventTrackerParameters } from '../definitions/InteractiveEventTrackerParameters';
import { trackEvent } from './trackEvent';

/**
 * trackSectionHidden is a shorthand for trackEvent. It eases triggering SectionHidden events programmatically
 */
export const trackSectionHidden = ({
  element,
  locationStack,
  globalContexts,
  tracker,
  onError,
}: InteractiveEventTrackerParameters) => {
  return trackEvent({
    event: makeSectionHiddenEvent({ location_stack: locationStack, global_contexts: globalContexts }),
    element,
    tracker,
    onError,
  });
};
