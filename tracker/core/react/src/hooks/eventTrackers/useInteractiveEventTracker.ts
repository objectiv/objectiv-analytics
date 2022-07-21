/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { trackInteractiveEvent } from '../../eventTrackers/trackInteractiveEvent';
import { EventTrackerHookCallbackParameters, EventTrackerHookParameters } from '../../types';
import { useLocationStack } from '../consumers/useLocationStack';
import { useTracker } from '../consumers/useTracker';
import { mergeEventTrackerHookAndCallbackParameters } from './mergeEventTrackerHookAndCallbackParameters';

/**
 * Returns an InteractiveEvent Tracker callback function, ready to be triggered.
 */
export const useInteractiveEventTracker = ({
  tracker = useTracker(),
  locationStack = [],
  ...hookParameters
}: EventTrackerHookParameters = {}) => {
  const combinedLocationStack = [...useLocationStack(), ...locationStack];

  return (callbackParameters: EventTrackerHookCallbackParameters = {}) =>
    trackInteractiveEvent(
      mergeEventTrackerHookAndCallbackParameters(
        { tracker, locationStack: combinedLocationStack, ...hookParameters },
        callbackParameters
      )
    );
};
