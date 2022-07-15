/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { makeInteractiveEvent } from '@objectiv/tracker-core';
import { EventTrackerParameters } from '../types';

/**
 * Factors an InteractiveEvent and hands it over to the given `tracker` via its `trackEvent` method.
 */
export const trackInteractiveEvent = ({ tracker, locationStack, globalContexts, options }: EventTrackerParameters) =>
  tracker.trackEvent(makeInteractiveEvent({ location_stack: locationStack, global_contexts: globalContexts }), options);
