/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { makeInputChangeEvent } from '@objectiv/tracker-core';
import { EventTrackerParameters } from '../types';

/**
 * Factors an InputChangeEvent and hands it over to the given `tracker` via its `trackEvent` method.
 */
export const trackInputChangeEvent = ({ tracker, locationStack, globalContexts, options }: EventTrackerParameters) =>
  tracker.trackEvent(makeInputChangeEvent({ location_stack: locationStack, global_contexts: globalContexts }), options);
