/*
 * Copyright 2021 Objectiv B.V.
 */

import { makeURLChangeEvent } from '@objectiv/tracker-core';
import { EventTrackerParameters } from '../types';

/**
 * Factors a URLChangeEvent and hands it over to the given `tracker` via its `trackEvent` method.
 */
export const trackURLChangeEvent = ({ tracker, locationStack, globalContexts, options }: EventTrackerParameters) =>
  tracker.trackEvent(makeURLChangeEvent({ location_stack: locationStack, global_contexts: globalContexts }), options);
