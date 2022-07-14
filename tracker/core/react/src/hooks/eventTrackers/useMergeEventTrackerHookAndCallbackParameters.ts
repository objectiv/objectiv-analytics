/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { EventTrackerHookCallbackParameters, EventTrackerHookParameters, EventTrackerParameters } from '../../types';
import { useLocationStack } from '../consumers/useLocationStack';
import { useTracker } from '../consumers/useTracker';

/**
 * A helper hook to merge the original parameter of a tracking hook with the parameters of their callbacks.
 * The resulting object is an EventTrackerParameters instance that can be directly fed to the low level APIs.
 * Some notes on the default values:
 * - Tracker instance: context provided Tracker < hook parameters Tracker < callback parameters Tracker
 * - Location stack is always composed by merging the context provided one with hook and cb, in this order
 * - Options are merged, callback options will take precedence over hook options with the same name
 */
export const useMergeEventTrackerHookAndCallbackParameters = (
  {
    tracker: hookTracker,
    locationStack: hookLocationStack,
    globalContexts: hookGlobalContexts,
    options: hookOptions,
  }: EventTrackerHookParameters,
  {
    tracker: cbTracker,
    locationStack: cbLocationStack,
    globalContexts: cbGlobalContexts,
    options: cbOptions,
  }: EventTrackerHookCallbackParameters
): EventTrackerParameters => {
  return {
    tracker: cbTracker ?? hookTracker ?? useTracker(),
    locationStack: [...useLocationStack(), ...(hookLocationStack ?? []), ...(cbLocationStack ?? [])],
    globalContexts: [...(hookGlobalContexts ?? []), ...(cbGlobalContexts ?? [])],
    options: hookOptions || cbOptions ? { ...(hookOptions ?? {}), ...(cbOptions ?? {}) } : undefined,
  };
};
