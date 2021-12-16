/*
 * Copyright 2021 Objectiv B.V.
 */

import { trackVideoPauseEvent } from '../../eventTrackers/trackVideoPauseEvent';
import { EventTrackerHookParameters } from '../../types';
import { useLocationStack } from '../consumers/useLocationStack';
import { useTracker } from '../consumers/useTracker';

/**
 * Returns a VideoPauseEvent Tracker callback function, ready to be triggered.
 */
export const useVideoPauseEventTracker = (parameters: EventTrackerHookParameters = {}) => {
  const { tracker = useTracker(), locationStack = useLocationStack(), globalContexts } = parameters;

  return () => trackVideoPauseEvent({ tracker, locationStack, globalContexts });
};
