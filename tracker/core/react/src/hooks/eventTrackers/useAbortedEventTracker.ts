/*
 * Copyright 2021 Objectiv B.V.
 */

import { trackAbortedEvent } from '../../eventTrackers/trackAbortedEvent';
import { EventTrackerHookParameters } from '../../types';
import { useLocationStack } from '../consumers/useLocationStack';
import { useTracker } from '../consumers/useTracker';

/**
 * Returns an AbortedEvent Tracker callback function, ready to be triggered.
 */
export const useAbortedEventTracker = (parameters: EventTrackerHookParameters = {}) => {
  const { tracker = useTracker(), locationStack = useLocationStack(), globalContexts } = parameters;

  return () => trackAbortedEvent({ tracker, locationStack, globalContexts });
};
