/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { makeVisibleEvent } from '@objectiv/tracker-core';
import { EventTrackerParameters } from '../types';

/**
 * Factors an VisibleEvent and hands it over to the given `tracker` via its `trackEvent` method.
 */
export const trackVisibleEvent = ({ tracker, locationStack, globalContexts, options }: EventTrackerParameters) =>
  tracker.trackEvent(makeVisibleEvent({ location_stack: locationStack, global_contexts: globalContexts }), options);
