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
export type TrackOnUnmountHookParameters = Partial<TrackEventParameters> & {
  /**
   * The Event to track
   */
  event: TrackerEventAttributes;
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
