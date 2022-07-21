/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { trackInputChangeEvent } from '../../eventTrackers/trackInputChangeEvent';
import { EventTrackerHookCallbackParameters, EventTrackerHookParameters } from '../../types';
import { useLocationStack } from '../consumers/useLocationStack';
import { useTracker } from '../consumers/useTracker';
import { mergeEventTrackerHookAndCallbackParameters } from './mergeEventTrackerHookAndCallbackParameters';

/**
 * Returns an InputChangeEvent Tracker callback function, ready to be triggered.
 */
export const useInputChangeEventTracker = ({
  tracker = useTracker(),
  locationStack = [],
  ...hookParameters
}: EventTrackerHookParameters = {}) => {
  const combinedLocationStack = [...useLocationStack(), ...locationStack];

  return (callbackParameters: EventTrackerHookCallbackParameters = {}) =>
    trackInputChangeEvent(
      mergeEventTrackerHookAndCallbackParameters(
        { tracker, locationStack: combinedLocationStack, ...hookParameters },
        callbackParameters
      )
    );
};
