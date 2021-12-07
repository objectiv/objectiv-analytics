/*
 * Copyright 2021 Objectiv B.V.
 */

import { APP_INITIALIZER, Provider } from '@angular/core';
import { BrowserTrackerConfig, makeTracker } from '@objectiv/tracker-browser';
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
 * Simply calls makeTracker
 */
export function ObjectivTrackerInitializer(trackerConfig: BrowserTrackerConfig) {
  return async () => {
    makeTracker(trackerConfig);
  };
}
