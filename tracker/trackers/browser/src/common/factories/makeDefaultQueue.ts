/*
 * Copyright 2021 Objectiv B.V.
 */

import { LocalStorageQueueStore } from '@objectiv/queue-local-storage';
import { TrackerQueue, TrackerQueueInterface } from '@objectiv/tracker-core';
import { BrowserTrackerConfig } from '../../definitions/BrowserTrackerConfig';

/**
 * A factory to create the default Queue of Browser Tracker.
 */
export const makeDefaultQueue = (trackerConfig: BrowserTrackerConfig): TrackerQueueInterface =>
  new TrackerQueue({
    store: new LocalStorageQueueStore({
      trackerId: trackerConfig.trackerId ?? trackerConfig.applicationId,
      console: trackerConfig.console,
    }),
    console: trackerConfig.console,
  });
