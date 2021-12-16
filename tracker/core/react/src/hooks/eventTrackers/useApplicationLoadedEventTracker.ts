/*
 * Copyright 2021 Objectiv B.V.
 */

import { trackApplicationLoadedEvent } from '../../eventTrackers/trackApplicationLoadedEvent';
import { EventTrackerHookParameters } from '../../types';
import { useLocationStack } from '../consumers/useLocationStack';
import { useTracker } from '../consumers/useTracker';

/**
 * Returns an ApplicationLoadedEvent Tracker callback function, ready to be triggered.
 */
export const useApplicationLoadedEventTracker = (parameters: EventTrackerHookParameters = {}) => {
  const { tracker = useTracker(), locationStack = useLocationStack(), globalContexts } = parameters;

  return () => trackApplicationLoadedEvent({ tracker, locationStack, globalContexts });
};
