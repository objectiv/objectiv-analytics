/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { makePressEvent } from '@objectiv/tracker-core';
import { EventTrackerParameters } from '../types';

/**
 * Factors a PressEvent and hands it over to the given `tracker` via its `trackEvent` method.
 */
export const trackPressEvent = ({ tracker, locationStack, globalContexts, options }: EventTrackerParameters) =>
  tracker.trackEvent(makePressEvent({ location_stack: locationStack, global_contexts: globalContexts }), options);
