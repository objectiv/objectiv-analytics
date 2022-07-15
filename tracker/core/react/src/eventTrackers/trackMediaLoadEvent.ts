/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { makeMediaLoadEvent } from '@objectiv/tracker-core';
import { EventTrackerParameters } from '../types';

/**
 * Factors an MediaLoadEvent and hands it over to the given `tracker` via its `trackEvent` method.
 */
export const trackMediaLoadEvent = ({ tracker, locationStack, globalContexts, options }: EventTrackerParameters) =>
  tracker.trackEvent(makeMediaLoadEvent({ location_stack: locationStack, global_contexts: globalContexts }), options);
