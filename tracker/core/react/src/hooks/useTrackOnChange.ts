/*
 * Copyright 2021 Objectiv B.V.
 */

import { TrackerEventConfig } from '@objectiv/tracker-core';
import { TrackEventParameters } from '../types';
import { useTracker } from './consumers/useTracker';
import { useOnChange } from './useOnChange';

/**
 * The parameters of useTrackOnChange
 */
export type TrackOnChangeHookParameters<T> = Partial<TrackEventParameters> & {
  /**
   * The variable this hook is going to be monitoring for changes
   */
  state: T;

  /**
   * The Event to track
   */
  event: TrackerEventConfig;
};

/**
 * A side effect that monitors the given `state` and triggers the given TrackerEvent when state changes.
 */
export const useTrackOnChange = <T>(parameters: TrackOnChangeHookParameters<T>) => {
  const { state, event, tracker = useTracker(), options } = parameters;

  return useOnChange<T>(state, () => {
    tracker.trackEvent(event, options);
  });
};
