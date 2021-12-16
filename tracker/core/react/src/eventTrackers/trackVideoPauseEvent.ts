/*
 * Copyright 2021 Objectiv B.V.
 */

import { makeVideoPauseEvent } from '@objectiv/tracker-core';
import { EventTrackerParameters } from '../types';

/**
 * Factors a VideoPauseEvent and hands it over to the given `tracker` via its `trackEvent` method.
 */
export const trackVideoPauseEvent = ({ tracker, locationStack, globalContexts, options }: EventTrackerParameters) =>
  tracker.trackEvent(makeVideoPauseEvent({ location_stack: locationStack, global_contexts: globalContexts }), options);
