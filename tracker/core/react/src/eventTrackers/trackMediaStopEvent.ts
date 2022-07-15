/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { makeMediaStopEvent } from '@objectiv/tracker-core';
import { EventTrackerParameters } from '../types';

/**
 * Factors a MediaStopEvent and hands it over to the given `tracker` via its `trackEvent` method.
 */
export const trackMediaStopEvent = ({ tracker, locationStack, globalContexts, options }: EventTrackerParameters) =>
  tracker.trackEvent(makeMediaStopEvent({ location_stack: locationStack, global_contexts: globalContexts }), options);
