/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { Optional } from '@objectiv/tracker-core';
import { SuccessEventTrackerParameters, trackSuccessEvent } from '../../eventTrackers/trackSuccessEvent';
import { EventTrackerHookParameters } from '../../types';
import { useMergeEventTrackerHookAndCallbackParameters } from './useMergeEventTrackerHookAndCallbackParameters';

/**
 * Returns a SuccessEvent Tracker callback function, ready to be triggered.
 */
export const useSuccessEventTracker =
  (hookParameters: EventTrackerHookParameters = {}) =>
  ({ message, ...callbackParameters }: Optional<SuccessEventTrackerParameters, 'tracker'>) =>
    trackSuccessEvent({
      message,
      ...useMergeEventTrackerHookAndCallbackParameters(hookParameters, callbackParameters),
    });
