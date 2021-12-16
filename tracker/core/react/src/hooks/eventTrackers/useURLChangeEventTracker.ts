/*
 * Copyright 2021 Objectiv B.V.
 */

import { trackURLChangeEvent } from '../../eventTrackers/trackURLChangeEvent';
import { EventTrackerHookParameters } from '../../types';
import { useLocationStack } from '../consumers/useLocationStack';
import { useTracker } from '../consumers/useTracker';

/**
 * Returns a URLChangeEvent Tracker callback function, ready to be triggered.
 */
export const useURLChangeEventTracker = (parameters: EventTrackerHookParameters = {}) => {
  const { tracker = useTracker(), locationStack = useLocationStack(), globalContexts } = parameters;

  return () => trackURLChangeEvent({ tracker, locationStack, globalContexts });
};
