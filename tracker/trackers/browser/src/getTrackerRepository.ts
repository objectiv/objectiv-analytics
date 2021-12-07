/*
 * Copyright 2021 Objectiv B.V.
 */

import { TrackerRepository } from '@objectiv/tracker-core';
import { BrowserTracker } from './BrowserTracker';
import { windowExists } from './common/windowExists';

/**
 * Retrieves the TrackerRepository instance from the window.objectiv global namespace
 */
export const getTrackerRepository = (): TrackerRepository<BrowserTracker> => {
  if (!windowExists()) {
    throw new Error('Cannot access the Window interface.');
  }

  return window.objectiv.trackers;
};
