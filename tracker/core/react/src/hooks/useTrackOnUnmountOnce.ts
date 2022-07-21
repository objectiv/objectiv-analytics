/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { TrackerEventAttributes } from '@objectiv/tracker-core';
import { TrackEventParameters } from '../types';
import { useTracker } from './consumers/useTracker';
import { useOnUnmount } from './useOnUnmount';

/**
 * The parameters of useTrackOnUnmount
 */
export type TrackOnUnmountOnceHookParameters = Partial<TrackEventParameters> & {
  /**
   * The Event to track
   */
  event: TrackerEventAttributes;
};

/**
 * A side effect that triggers the given TrackerEvent once on unmount.
 * Uses a ref instead of deps for compatibility with React 18.
 */
export const useTrackOnUnmountOnce = (parameters: TrackOnUnmountOnceHookParameters) => {
  const { event, tracker = useTracker(), options } = parameters;

  return useOnUnmount(() => {
    tracker.trackEvent(event, options);
  });
};
