import { InjectionToken } from '@angular/core';
import { BrowserTrackerConfig } from '@objectiv/tracker-browser';

export const OBJECTIV_TRACKER_CONFIG_TOKEN = new InjectionToken<BrowserTrackerConfig>('objectiv-tracker-config', {
  factory: () => ({ applicationId: '' }),
});
