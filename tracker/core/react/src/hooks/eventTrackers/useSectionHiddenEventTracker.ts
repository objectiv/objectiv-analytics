/*
 * Copyright 2021 Objectiv B.V.
 */

import { trackSectionHiddenEvent } from '../../eventTrackers/trackSectionHiddenEvent';
import { EventTrackerHookParameters } from '../../types';
import { useLocationStack } from '../consumers/useLocationStack';
import { useTracker } from '../consumers/useTracker';

/**
 * Returns a SectionHiddenEvent Tracker callback function, ready to be triggered.
 */
export const useSectionHiddenEventTracker = (parameters: EventTrackerHookParameters = {}) => {
  const { tracker = useTracker(), locationStack = useLocationStack(), globalContexts } = parameters;

  return () => trackSectionHiddenEvent({ tracker, locationStack, globalContexts });
};
