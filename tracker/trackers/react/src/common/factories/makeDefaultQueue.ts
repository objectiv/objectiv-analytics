/*
 * Copyright 2021 Objectiv B.V.
 */

import { TrackerQueue, TrackerQueueInterface } from '@objectiv/tracker-core';
import { TrackerQueueLocalStorage } from '../../queues/TrackerQueueLocalStorage';
import { ReactTrackerConfig } from '../../ReactTracker';

/**
 * A factory to create the default Queue of React Tracker.
 */
export const makeDefaultQueue = (trackerConfig: ReactTrackerConfig): TrackerQueueInterface =>
  new TrackerQueue({
    store: new TrackerQueueLocalStorage({
      trackerId: trackerConfig.trackerId ?? trackerConfig.applicationId,
      console: trackerConfig.console,
    }),
    console: trackerConfig.console,
  });
