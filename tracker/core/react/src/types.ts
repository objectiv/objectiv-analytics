/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { GlobalContexts, LocationStack, Optional, Tracker, TrackEventOptions } from '@objectiv/tracker-core';
import { useEffect } from 'react';

/**
 * A custom generic EffectCallback that receives the monitored `previousState` and `state` values
 */
export type OnChangeEffectCallback<T> = (previousState: T, state: T) => void;

/**
 * A custom EffectCallback that receives the monitored `previousState` and `state` boolean values
 */
export type OnToggleEffectCallback = (previousState: boolean, state: boolean) => void;

/**
 * A useEffect Destructor
 */
export type EffectDestructor = () => ReturnType<typeof useEffect>;

/**
 * Common parameters that all Tracker.trackEvent functions and hook should support
 */
export type TrackEventParameters = {
  /**
   * A Tracker instance.
   */
  tracker: Tracker;

  /**
   * Optional. Tracker.trackEvent options. Allows configuring whether to wait and/or flush the Tracker Queue.
   */
  options?: TrackEventOptions;
};

/**
 * The parameters of Event Tracker shorthand functions
 */
export type EventTrackerParameters = TrackEventParameters & {
  /**
   * Optional. Additional Location Contexts to merge in the Event's LocationStack
   */
  locationStack?: LocationStack;

  /**
   * Optional. Additional Location Contexts to merge in the Event's GlobalContexts
   */
  globalContexts?: GlobalContexts;
};

/**
 * The base parameters of all EventTracker hooks.
 * Same as EventTrackerParameters but everything is optional.
 * Hooks will be automatically invoked to retrieve a Tracker instance and LocationStack.
 */
export type EventTrackerHookParameters = Partial<EventTrackerParameters>;

/**
 * The base parameters of all EventTracker hooks' callbacks.
 * The `tracker` attribute is optional. Hooks automatically retrieve Tracker instance.
 */
export type EventTrackerHookCallbackParameters = Optional<EventTrackerHookParameters, 'tracker'>;
