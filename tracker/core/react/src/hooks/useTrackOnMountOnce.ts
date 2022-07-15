/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { TrackerEventAttributes } from '@objectiv/tracker-core';
import { TrackEventParameters } from '../types';
import { useTracker } from './consumers/useTracker';
import { useOnMountOnce } from './useOnMountOnce';

/**
 * The parameters of useTrackOnMount
 */
export type TrackOnMountOnceHookParameters = Partial<TrackEventParameters> & {
  /**
   * The Event to track
   */
  event: TrackerEventAttributes;
};

/**
 * A side effect that triggers the given TrackerEvent once on mount.
 * Uses a ref instead of deps for compatibility with React 18.
 */
export const useTrackOnMountOnce = (parameters: TrackOnMountOnceHookParameters) => {
  const { event, tracker = useTracker(), options } = parameters;

  return useOnMountOnce(() => {
    tracker.trackEvent(event, options);
  });
};
