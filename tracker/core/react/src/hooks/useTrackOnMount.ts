/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { TrackerEventAttributes } from '@objectiv/tracker-core';
import { TrackEventParameters } from '../types';
import { useTracker } from './consumers/useTracker';
import { useOnMount } from './useOnMount';

/**
 * The parameters of useTrackOnMount
 */
export type TrackOnMountHookParameters = Partial<TrackEventParameters> & {
  /**
   * The Event to track
   */
  event: TrackerEventAttributes;
};

/**
 * A side effect that triggers the given TrackerEvent on mount.
 */
export const useTrackOnMount = (parameters: TrackOnMountHookParameters) => {
  const { event, tracker = useTracker(), options } = parameters;

  return useOnMount(() => {
    tracker.trackEvent(event, options);
  });
};
