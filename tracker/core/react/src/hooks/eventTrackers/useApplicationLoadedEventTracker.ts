/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { trackApplicationLoadedEvent } from '../../eventTrackers/trackApplicationLoadedEvent';
import { EventTrackerHookCallbackParameters, EventTrackerHookParameters } from '../../types';
import { useMergeEventTrackerHookAndCallbackParameters } from './useMergeEventTrackerHookAndCallbackParameters';

/**
 * Returns an ApplicationLoadedEvent Tracker callback function, ready to be triggered.
 */
export const useApplicationLoadedEventTracker =
  (hookParameters: EventTrackerHookParameters = {}) =>
  (callbackParameters: EventTrackerHookCallbackParameters = {}) =>
    trackApplicationLoadedEvent(useMergeEventTrackerHookAndCallbackParameters(hookParameters, callbackParameters));
