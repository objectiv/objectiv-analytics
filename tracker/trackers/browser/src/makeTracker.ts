/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { BrowserTracker } from './BrowserTracker';
import { BrowserTrackerConfig } from './definitions/BrowserTrackerConfig';
import { startAutoTracking } from './startAutoTracking';

/**
 * Allows to easily create and configure a new BrowserTracker instance and also starts auto tracking
 */
export const makeTracker = (trackerConfig: BrowserTrackerConfig): BrowserTracker => {
  const newTracker = new BrowserTracker(trackerConfig);

  startAutoTracking(trackerConfig);

  return newTracker;
};
