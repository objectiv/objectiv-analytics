/*
 * Copyright 2021 Objectiv B.V.
 */

import { makeVideoStartEvent } from '@objectiv/tracker-core';
import { EventTrackerParameters } from '../types';

/**
 * Factors a VideoStartEvent and hands it over to the given `tracker` via its `trackEvent` method.
 */
export const trackVideoStartEvent = ({ tracker, locationStack, globalContexts, options }: EventTrackerParameters) =>
  tracker.trackEvent(makeVideoStartEvent({ location_stack: locationStack, global_contexts: globalContexts }), options);
