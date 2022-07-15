/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { Optional } from '@objectiv/tracker-core';
import { FailureEventTrackerParameters, trackFailureEvent } from '../../eventTrackers/trackFailureEvent';
import { EventTrackerHookParameters } from '../../types';
import { useLocationStack } from '../consumers/useLocationStack';
import { useTracker } from '../consumers/useTracker';
import { mergeEventTrackerHookAndCallbackParameters } from './mergeEventTrackerHookAndCallbackParameters';

/**
 * Returns an FailureEvent Tracker callback function, ready to be triggered.
 */
export const useFailureEventTracker = ({
  tracker = useTracker(),
  locationStack = [],
  ...hookParameters
}: EventTrackerHookParameters = {}) => {
  const combinedLocationStack = [...useLocationStack(), ...locationStack];

  return ({ message, ...callbackParameters }: Optional<FailureEventTrackerParameters, 'tracker'>) =>
    trackFailureEvent({
      message,
      ...mergeEventTrackerHookAndCallbackParameters(
        {
          tracker,
          locationStack: combinedLocationStack,
          ...hookParameters,
        },
        callbackParameters
      ),
    });
};
