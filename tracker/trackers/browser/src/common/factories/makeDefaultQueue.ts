/*
 * Copyright 2021 Objectiv B.V.
 */

import { TrackerQueue, TrackerQueueInterface } from '@objectiv/tracker-core';
import { BrowserTrackerConfig } from '../../definitions/BrowserTrackerConfig';
import { TrackerQueueLocalStorage } from '../../queues/TrackerQueueLocalStorage';

/**
 * A factory to create the default Queue of Browser Tracker.
 */
export const makeDefaultQueue = (trackerConfig: BrowserTrackerConfig): TrackerQueueInterface =>
  new TrackerQueue({
    store: new TrackerQueueLocalStorage({
      trackerId: trackerConfig.trackerId ?? trackerConfig.applicationId,
      console: trackerConfig.console,
    }),
    console: trackerConfig.console,
  });
