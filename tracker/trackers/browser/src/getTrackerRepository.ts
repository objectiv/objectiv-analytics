/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { TrackerRepositoryInterface } from '@objectiv/tracker-core';
import { BrowserTracker } from './BrowserTracker';

/**
 * Retrieves the TrackerRepository
 */
export const getTrackerRepository = (): TrackerRepositoryInterface<BrowserTracker> => {
  return globalThis.objectiv.TrackerRepository as TrackerRepositoryInterface<BrowserTracker>;
};
