/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { trackVisibility, TrackVisibilityParameters } from '../../eventTrackers/trackVisibility';
import { EventTrackerHookParameters } from '../../types';
import { useLocationStack } from '../consumers/useLocationStack';
import { useTracker } from '../consumers/useTracker';

/**
 * Returns a VisibleEvent / HiddenEvent Tracker ready to be triggered.
 * The `isVisible` parameter determines which Visibility Event is triggered.
 */
export const useVisibilityTracker = (parameters: EventTrackerHookParameters = {}) => {
  const { tracker = useTracker(), locationStack = useLocationStack(), globalContexts } = parameters;

  return ({ isVisible }: Pick<TrackVisibilityParameters, 'isVisible'>) =>
    trackVisibility({ isVisible, tracker, locationStack, globalContexts });
};
