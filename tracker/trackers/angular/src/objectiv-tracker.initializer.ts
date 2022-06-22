/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { APP_INITIALIZER, Provider } from '@angular/core';
import { BrowserTrackerConfig, startAutoTracking } from '@objectiv/tracker-browser';
import { AngularTracker } from './AngularTracker';
import { OBJECTIV_TRACKER_CONFIG_TOKEN } from './objectiv-tracker.token';

/**
 * DI Configuration to attach Tracker Initialization.
 */
export const OBJECTIV_TRACKER_INITIALIZER_PROVIDER: Provider = {
  provide: APP_INITIALIZER,
  multi: true,
  useFactory: ObjectivTrackerInitializer,
  deps: [OBJECTIV_TRACKER_CONFIG_TOKEN],
};

/**
 * Simply create a new AngularTracker instance and starts the auto-tracking MutationObserver.
 */
export function ObjectivTrackerInitializer(trackerConfig: BrowserTrackerConfig) {
  return async () => {
    const newTracker = new AngularTracker(trackerConfig);

    startAutoTracking(trackerConfig);

    return newTracker;
  };
}
