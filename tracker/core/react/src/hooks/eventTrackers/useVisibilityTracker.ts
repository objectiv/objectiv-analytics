/*
 * Copyright 2021 Objectiv B.V.
 */

import { trackVisibility } from '../../eventTrackers/trackVisibility';
import { EventTrackerHookParameters } from '../../types';
import { useLocationStack } from '../consumers/useLocationStack';
import { useTracker } from '../consumers/useTracker';

/**
 * The parameters of `useTrackVisibility`
 */
export type TrackVisibilityHookParameters = EventTrackerHookParameters & {
  /**
   * Determines whether a SectionVisibleEvent or a SectionHidden event is tracked
   */
  isVisible: boolean;
};

/**
 * Returns a SectionVisibleEvent / SectionHiddenEvent Tracker ready to be triggered.
 * The `isVisible` parameter determines which Visibility Event is triggered.
 */
export const useVisibilityTracker = (parameters: TrackVisibilityHookParameters) => {
  const { isVisible, tracker = useTracker(), locationStack = useLocationStack(), globalContexts } = parameters;

  return () => trackVisibility({ isVisible, tracker, locationStack, globalContexts });
};
