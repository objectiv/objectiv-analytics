/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { SuccessEventTrackerParameters, trackSuccessEvent } from '../../eventTrackers/trackSuccessEvent';
import { EventTrackerHookParameters } from '../../types';
import { useLocationStack } from '../consumers/useLocationStack';
import { useTracker } from '../consumers/useTracker';

/**
 * Returns a SuccessEvent Tracker callback function, ready to be triggered.
 */
export const useSuccessEventTracker = (parameters: EventTrackerHookParameters = {}) => {
  const { tracker = useTracker(), locationStack = useLocationStack(), globalContexts = [], options } = parameters;

  return ({
    message,
    locationStack: extraLocationStack = [],
    globalContexts: extraGlobalContexts = [],
    options: extraOptions,
  }: Omit<SuccessEventTrackerParameters, 'tracker'>) =>
    trackSuccessEvent({
      message,
      tracker,
      options: options || extraOptions ? { ...(options ?? {}), ...(extraOptions ?? {}) } : undefined,
      locationStack: [...locationStack, ...extraLocationStack],
      globalContexts: [...globalContexts, ...extraGlobalContexts],
    });
};
