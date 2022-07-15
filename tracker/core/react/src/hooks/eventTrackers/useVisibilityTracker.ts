/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { Optional } from '@objectiv/tracker-core';
import { trackVisibility, TrackVisibilityParameters } from '../../eventTrackers/trackVisibility';
import { EventTrackerHookParameters } from '../../types';
import { useLocationStack } from '../consumers/useLocationStack';
import { useTracker } from '../consumers/useTracker';
import { mergeEventTrackerHookAndCallbackParameters } from './mergeEventTrackerHookAndCallbackParameters';

/**
 * Returns a VisibleEvent / HiddenEvent Tracker ready to be triggered.
 * The `isVisible` parameter determines which Visibility Event is triggered.
 */
export const useVisibilityTracker = ({
  tracker = useTracker(),
  locationStack = [],
  ...hookParameters
}: EventTrackerHookParameters = {}) => {
  const combinedLocationStack = [...useLocationStack(), ...locationStack];

  return ({ isVisible, ...callbackParameters }: Optional<TrackVisibilityParameters, 'tracker'>) =>
    trackVisibility({
      isVisible,
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
