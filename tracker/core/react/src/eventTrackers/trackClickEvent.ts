/*
 * Copyright 2021 Objectiv B.V.
 */

import { makeClickEvent } from '@objectiv/tracker-core';
import { EventTrackerParameters } from '../types';

/**
 * Factors a ClickEvent and hands it over to the given `tracker` via its `trackEvent` method.
 */
export const trackClickEvent = ({ tracker, locationStack, globalContexts, options }: EventTrackerParameters) =>
  tracker.trackEvent(makeClickEvent({ location_stack: locationStack, global_contexts: globalContexts }), options);
