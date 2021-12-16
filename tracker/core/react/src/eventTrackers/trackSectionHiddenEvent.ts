/*
 * Copyright 2021 Objectiv B.V.
 */

import { makeSectionHiddenEvent } from '@objectiv/tracker-core';
import { EventTrackerParameters } from '../types';

/**
 * Factors a SectionHiddenEvent and hands it over to the given `tracker` via its `trackEvent` method.
 */
export const trackSectionHiddenEvent = ({ tracker, locationStack, globalContexts, options }: EventTrackerParameters) =>
  tracker.trackEvent(
    makeSectionHiddenEvent({ location_stack: locationStack, global_contexts: globalContexts }),
    options
  );
