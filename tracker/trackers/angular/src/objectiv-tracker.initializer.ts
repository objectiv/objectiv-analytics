/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { APP_INITIALIZER, Provider } from '@angular/core';
import { BrowserTrackerConfig, getTrackerRepository, startAutoTracking } from '@objectiv/tracker-browser';
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
 * Simply calls makeTracker
 */
export function ObjectivTrackerInitializer(trackerConfig: BrowserTrackerConfig) {
  return async () => {
    const newTracker = new AngularTracker(trackerConfig);
    const trackerRepository = getTrackerRepository();

    trackerRepository.add(newTracker);
    startAutoTracking(trackerConfig);

    return newTracker;
  };
}
