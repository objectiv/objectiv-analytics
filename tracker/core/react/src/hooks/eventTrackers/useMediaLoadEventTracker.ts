/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { trackMediaLoadEvent } from '../../eventTrackers/trackMediaLoadEvent';
import { EventTrackerHookCallbackParameters, EventTrackerHookParameters } from '../../types';
import { useLocationStack } from '../consumers/useLocationStack';
import { useTracker } from '../consumers/useTracker';
import { mergeEventTrackerHookAndCallbackParameters } from './mergeEventTrackerHookAndCallbackParameters';

/**
 * Returns a MediaLoadEvent Tracker callback function, ready to be triggered.
 */
export const useMediaLoadEventTracker = ({
  tracker = useTracker(),
  locationStack = [],
  ...hookParameters
}: EventTrackerHookParameters = {}) => {
  const combinedLocationStack = [...useLocationStack(), ...locationStack];

  return (callbackParameters: EventTrackerHookCallbackParameters = {}) =>
    trackMediaLoadEvent(
      mergeEventTrackerHookAndCallbackParameters(
        { tracker, locationStack: combinedLocationStack, ...hookParameters },
        callbackParameters
      )
    );
};
