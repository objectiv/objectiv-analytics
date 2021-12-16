/*
 * Copyright 2021 Objectiv B.V.
 */

import { AbstractLocationContext } from '@objectiv/schema';
import { GlobalContexts, Tracker, TrackEventOptions } from '@objectiv/tracker-core';
import { useEffect } from 'react';

/**
 * A uniquely identifiable LocationContext
 */
export type LocationContext<T extends AbstractLocationContext> = T & {
  /**
   * A unique identifier, generated at rendering time, used internally to identify a Location Context uniquely
   */
  __location_id: string;
};

/**
 * An ordered list of uniquely identifiable LocationContexts
 */
export type LocationStack = LocationContext<AbstractLocationContext>[];

/**
 * A custom generic EffectCallback that receives the monitored `previousState` and `state` values
 */
export type OnChangeEffectCallback = <T>(previousState: T, state: T) => void;

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
