/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { makeMediaStartEvent } from '@objectiv/tracker-core';
import { EventTrackerParameters } from '../types';

/**
 * Factors a MediaStartEvent and hands it over to the given `tracker` via its `trackEvent` method.
 */
export const trackMediaStartEvent = ({ tracker, locationStack, globalContexts, options }: EventTrackerParameters) =>
  tracker.trackEvent(makeMediaStartEvent({ location_stack: locationStack, global_contexts: globalContexts }), options);
