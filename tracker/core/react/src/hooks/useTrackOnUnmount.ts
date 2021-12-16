/*
 * Copyright 2021 Objectiv B.V.
 */

import { TrackerEventConfig } from '@objectiv/tracker-core';
import { TrackEventParameters } from '../types';
import { useTracker } from './consumers/useTracker';
import { useOnUnmount } from './useOnUnmount';

/**
 * The parameters of useTrackOnUnmount
 */
export type TrackOnUnmountHookParameters = Partial<TrackEventParameters> & {
  /**
   * The Event to track
   */
  event: TrackerEventConfig;
};

/**
 * A side effect that triggers the given TrackerEvent on unmount.
 */
export const useTrackOnUnmount = (parameters: TrackOnUnmountHookParameters) => {
  const { event, tracker = useTracker(), options } = parameters;

  return useOnUnmount(() => {
    tracker.trackEvent(event, options);
  });
};
