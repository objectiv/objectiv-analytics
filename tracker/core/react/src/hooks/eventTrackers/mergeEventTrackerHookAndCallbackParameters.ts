/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { EventTrackerHookCallbackParameters, EventTrackerParameters } from '../../types';

/**
 * A helper hook to merge the original parameter of a tracking hook with the parameters of their callbacks.
 * The resulting object is an EventTrackerParameters instance that can be directly fed to the low level APIs.
 * Some notes on the default values:
 * - Tracker instance: context provided Tracker < hook parameters Tracker
 * - Location stack is always composed by merging the hook and cb location stacks, in this order
 * - Options are merged, callback options will take precedence over hook options with the same name
 */
export const mergeEventTrackerHookAndCallbackParameters = (
  {
    tracker: hookTracker,
    locationStack: hookLocationStack,
    globalContexts: hookGlobalContexts,
    options: hookOptions,
  }: EventTrackerParameters,
  {
    tracker: cbTracker,
    locationStack: cbLocationStack,
    globalContexts: cbGlobalContexts,
    options: cbOptions,
  }: EventTrackerHookCallbackParameters
): EventTrackerParameters => {
  return {
    tracker: cbTracker ?? hookTracker,
    locationStack: [...(hookLocationStack ?? []), ...(cbLocationStack ?? [])],
    globalContexts: [...(hookGlobalContexts ?? []), ...(cbGlobalContexts ?? [])],
    options: hookOptions || cbOptions ? { ...(hookOptions ?? {}), ...(cbOptions ?? {}) } : undefined,
  };
};
