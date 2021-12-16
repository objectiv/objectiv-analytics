/*
 * Copyright 2021 Objectiv B.V.
 */

import { trackInputChangeEvent } from '../../eventTrackers/trackInputChangeEvent';
import { EventTrackerHookParameters } from '../../types';
import { useLocationStack } from '../consumers/useLocationStack';
import { useTracker } from '../consumers/useTracker';

/**
 * Returns an InputChangeEvent Tracker callback function, ready to be triggered.
 */
export const useInputChangeEventTracker = (parameters: EventTrackerHookParameters = {}) => {
  const { tracker = useTracker(), locationStack = useLocationStack(), globalContexts } = parameters;

  return () => trackInputChangeEvent({ tracker, locationStack, globalContexts });
};
