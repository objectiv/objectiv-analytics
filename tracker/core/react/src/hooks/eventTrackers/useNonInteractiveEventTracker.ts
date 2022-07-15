/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { trackNonInteractiveEvent } from '../../eventTrackers/trackNonInteractiveEvent';
import { EventTrackerHookCallbackParameters, EventTrackerHookParameters } from '../../types';
import { useLocationStack } from '../consumers/useLocationStack';
import { useTracker } from '../consumers/useTracker';
import { mergeEventTrackerHookAndCallbackParameters } from './mergeEventTrackerHookAndCallbackParameters';

/**
 * Returns an NonInteractiveEvent Tracker callback function, ready to be triggered.
 */
export const useNonInteractiveEventTracker = ({
  tracker = useTracker(),
  locationStack = [],
  ...hookParameters
}: EventTrackerHookParameters = {}) => {
  const combinedLocationStack = [...useLocationStack(), ...locationStack];

  return (callbackParameters: EventTrackerHookCallbackParameters = {}) =>
    trackNonInteractiveEvent(
      mergeEventTrackerHookAndCallbackParameters(
        { tracker, locationStack: combinedLocationStack, ...hookParameters },
        callbackParameters
      )
    );
};
