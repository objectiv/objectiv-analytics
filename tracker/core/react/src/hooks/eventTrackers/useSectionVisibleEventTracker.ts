/*
 * Copyright 2021 Objectiv B.V.
 */

import { trackSectionVisibleEvent } from '../../eventTrackers/trackSectionVisibleEvent';
import { EventTrackerHookParameters } from '../../types';
import { useLocationStack } from '../consumers/useLocationStack';
import { useTracker } from '../consumers/useTracker';

/**
 * Returns a SectionVisibleEvent Tracker callback function, ready to be triggered.
 */
export const useSectionVisibleEventTracker = (parameters: EventTrackerHookParameters = {}) => {
  const { tracker = useTracker(), locationStack = useLocationStack(), globalContexts } = parameters;

  return () => trackSectionVisibleEvent({ tracker, locationStack, globalContexts });
};
