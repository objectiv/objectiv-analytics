/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { makeMediaEvent } from '@objectiv/tracker-core';
import { EventTrackerParameters } from '../types';

/**
 * Factors an MediaEvent and hands it over to the given `tracker` via its `trackEvent` method.
 */
export const trackMediaEvent = ({ tracker, locationStack, globalContexts, options }: EventTrackerParameters) =>
  tracker.trackEvent(makeMediaEvent({ location_stack: locationStack, global_contexts: globalContexts }), options);
