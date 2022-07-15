/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { UntrackedEventConfig } from '@objectiv/tracker-core';
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
  trueEvent: UntrackedEventConfig;

  /**
   * The Event to track when state changes from `true` to `false`
   */
  falseEvent: UntrackedEventConfig;
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
