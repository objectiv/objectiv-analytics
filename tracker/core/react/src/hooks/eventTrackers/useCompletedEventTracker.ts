/*
 * Copyright 2021 Objectiv B.V.
 */

import { trackCompletedEvent } from '../../eventTrackers/trackCompletedEvent';
import { EventTrackerHookParameters } from '../../types';
import { useLocationStack } from '../consumers/useLocationStack';
import { useTracker } from '../consumers/useTracker';

/**
 * Returns a CompletedEvent Tracker callback function, ready to be triggered.
 */
export const useCompletedEventTracker = (parameters: EventTrackerHookParameters = {}) => {
  const { tracker = useTracker(), locationStack = useLocationStack(), globalContexts } = parameters;

  return () => trackCompletedEvent({ tracker, locationStack, globalContexts });
};
