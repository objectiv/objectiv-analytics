/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { trackFailureEvent } from '../../eventTrackers/trackFailureEvent';
import { SuccessEventTrackerParameters } from '../../eventTrackers/trackSuccessEvent';
import { EventTrackerHookParameters } from '../../types';
import { useLocationStack } from '../consumers/useLocationStack';
import { useTracker } from '../consumers/useTracker';

/**
 * Returns an FailureEvent Tracker callback function, ready to be triggered.
 */
export const useFailureEventTracker = (parameters: EventTrackerHookParameters = {}) => {
  const { tracker = useTracker(), locationStack = useLocationStack(), globalContexts } = parameters;

  return ({ message }: Pick<SuccessEventTrackerParameters, 'message'>) =>
    trackFailureEvent({ message, tracker, locationStack, globalContexts });
};
