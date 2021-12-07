/*
 * Copyright 2021 Objectiv B.V.
 */

import { ModuleWithProviders, NgModule } from '@angular/core';
import { BrowserTrackerConfig } from '@objectiv/tracker-browser';
import { ObjectivTrackerDirective } from './objectiv-tracker.directive';
import { OBJECTIV_TRACKER_INITIALIZER_PROVIDER } from './objectiv-tracker.initializer';
import { OBJECTIV_TRACKER_CONFIG_TOKEN } from './objectiv-tracker.token';

/**
 * Configures Objectiv Tracker.
 * This module is meant to be set as a dependency of the highest level module of the application, such as AppModule.
 */
@NgModule({
  imports: [],
  declarations: [ObjectivTrackerDirective],
  exports: [ObjectivTrackerDirective],
})
export class ObjectivTrackerModule {
  static forRoot(trackerConfig: BrowserTrackerConfig): ModuleWithProviders<ObjectivTrackerModule> {
    return {
      ngModule: ObjectivTrackerModule,
      providers: [
        {
          provide: OBJECTIV_TRACKER_CONFIG_TOKEN,
          useValue: trackerConfig,
        },
        OBJECTIV_TRACKER_INITIALIZER_PROVIDER,
      ],
    };
  }
}
