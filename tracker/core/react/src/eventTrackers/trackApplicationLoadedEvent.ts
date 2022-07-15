/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { makeApplicationLoadedEvent } from '@objectiv/tracker-core';
import { EventTrackerParameters } from '../types';

/**
 * Factors an ApplicationLoadedEvent and hands it over to the given `tracker` via its `trackEvent` method.
 */
export const trackApplicationLoadedEvent = ({
  tracker,
  locationStack,
  globalContexts,
  options,
}: EventTrackerParameters) =>
  tracker.trackEvent(
    makeApplicationLoadedEvent({ location_stack: locationStack, global_contexts: globalContexts }),
    options
  );
