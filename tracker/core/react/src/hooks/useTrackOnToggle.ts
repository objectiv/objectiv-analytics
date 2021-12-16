/*
 * Copyright 2021 Objectiv B.V.
 */

import { TrackerEventConfig } from '@objectiv/tracker-core';
import { TrackEventParameters } from '../types';
import { useTracker } from './consumers/useTracker';
import { useOnToggle } from './useOnToggle';

/**
 * The parameters of useTrackOnToggle
 */
export type TrackOnToggleHookParameters = Partial<TrackEventParameters> & {
  /**
   * A boolean variable this hook is going to be monitoring for determining when and which event to trigger
   */
  state: boolean;

  /**
   * The Event to track when state changes from `false` to `true`
   */
  trueEvent: TrackerEventConfig;

  /**
   * The Event to track when state changes from `true` to `false`
   */
  falseEvent: TrackerEventConfig;
};

/**
 * A variant of the trackOnChange side effect that monitors a boolean `state` and runs the given `trueEvent` or
 * `falseEvent` depending on the state value.
 **/
export const useTrackOnToggle = (parameters: TrackOnToggleHookParameters) => {
  const { state, trueEvent, falseEvent, tracker = useTracker(), options } = parameters;

  return useOnToggle(
    state,
    () => tracker.trackEvent(trueEvent, options),
    () => tracker.trackEvent(falseEvent, options)
  );
};
