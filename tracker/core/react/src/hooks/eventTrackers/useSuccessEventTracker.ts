/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { Optional } from '@objectiv/tracker-core';
import { SuccessEventTrackerParameters, trackSuccessEvent } from '../../eventTrackers/trackSuccessEvent';
import { EventTrackerHookParameters } from '../../types';
import { useLocationStack } from '../consumers/useLocationStack';
import { useTracker } from '../consumers/useTracker';
import { mergeEventTrackerHookAndCallbackParameters } from './mergeEventTrackerHookAndCallbackParameters';

/**
 * Returns a SuccessEvent Tracker callback function, ready to be triggered.
 */
export const useSuccessEventTracker = ({
  tracker = useTracker(),
  locationStack = [],
  ...hookParameters
}: EventTrackerHookParameters = {}) => {
  const combinedLocationStack = [...useLocationStack(), ...locationStack];

  return ({ message, ...callbackParameters }: Optional<SuccessEventTrackerParameters, 'tracker'>) =>
    trackSuccessEvent({
      message,
      ...mergeEventTrackerHookAndCallbackParameters(
        { tracker, locationStack: combinedLocationStack, ...hookParameters },
        callbackParameters
      ),
    });
};
