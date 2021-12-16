/*
 * Copyright 2021 Objectiv B.V.
 */

import { makeSectionHiddenEvent, makeSectionVisibleEvent } from '@objectiv/tracker-core';
import { EventTrackerParameters } from '../types';

/**
 * The parameters of `trackVisibility`
 */
export type TrackVisibilityParameters = EventTrackerParameters & {
  /**
   * Determines whether a SectionVisibleEvent or a SectionHidden event is tracked
   */
  isVisible: boolean;
};

/**
 * Factors either a SectionVisibleEvent or a SectionHiddenEvent, depending on the given `isVisible` parameter, and
 * hands it over to the given `tracker` via its `trackEvent` method.
 */
export const trackVisibility = ({
  tracker,
  isVisible,
  locationStack,
  globalContexts,
  options,
}: TrackVisibilityParameters) => {
  const extraContexts = { location_stack: locationStack, global_contexts: globalContexts };

  return tracker.trackEvent(
    isVisible ? makeSectionVisibleEvent(extraContexts) : makeSectionHiddenEvent(extraContexts),
    options
  );
};
