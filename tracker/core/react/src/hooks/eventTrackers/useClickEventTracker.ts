/*
 * Copyright 2021 Objectiv B.V.
 */

import { trackClickEvent } from '../../eventTrackers/trackClickEvent';
import { EventTrackerHookParameters } from '../../types';
import { useLocationStack } from '../consumers/useLocationStack';
import { useTracker } from '../consumers/useTracker';

/**
 * Returns a ClickEvent Tracker callback function, ready to be triggered.
 */
export const useClickEventTracker = (parameters: EventTrackerHookParameters = {}) => {
  const { tracker = useTracker(), locationStack = useLocationStack(), globalContexts } = parameters;

  return () => trackClickEvent({ tracker, locationStack, globalContexts });
};
