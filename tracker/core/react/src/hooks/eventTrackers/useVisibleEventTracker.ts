/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { trackVisibleEvent } from '../../eventTrackers/trackVisibleEvent';
import { EventTrackerHookCallbackParameters, EventTrackerHookParameters } from '../../types';
import { useLocationStack } from '../consumers/useLocationStack';
import { useTracker } from '../consumers/useTracker';
import { mergeEventTrackerHookAndCallbackParameters } from './mergeEventTrackerHookAndCallbackParameters';

/**
 * Returns a VisibleEvent Tracker callback function, ready to be triggered.
 */
export const useVisibleEventTracker = ({
  tracker = useTracker(),
  locationStack = [],
  ...hookParameters
}: EventTrackerHookParameters = {}) => {
  const combinedLocationStack = [...useLocationStack(), ...locationStack];

  return (callbackParameters: EventTrackerHookCallbackParameters = {}) =>
    trackVisibleEvent(
      mergeEventTrackerHookAndCallbackParameters(
        { tracker, locationStack: combinedLocationStack, ...hookParameters },
        callbackParameters
      )
    );
};
