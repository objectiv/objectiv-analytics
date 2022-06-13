/*
 * Copyright 2022 Objectiv B.V.
 */

import {
  BrowserTrackerConfig,
  ContextsConfig,
  isPluginsArray,
  makeBrowserTrackerDefaultPluginsList,
  makeBrowserTrackerDefaultQueue,
  makeBrowserTrackerDefaultTransport,
  Tracker,
  TrackerConfig,
} from '@objectiv/tracker-browser';
import { TrackerPlatform } from '@objectiv/tracker-core';

/**
 * Angular Tracker is identical to BrowserTracker, exception made for its platform.
 */
export class AngularTracker extends Tracker {
  // A copy of the original configuration
  readonly trackerConfig: TrackerConfig;

  constructor(trackerConfig: BrowserTrackerConfig, ...contextConfigs: ContextsConfig[]) {
    let config: TrackerConfig = trackerConfig;

    // Set the platform
    config.platform = TrackerPlatform.ANGULAR;

    // Either `transport` or `endpoint` must be provided
    if (!config.transport && !trackerConfig.endpoint) {
      throw new Error('Either `transport` or `endpoint` must be provided');
    }

    // `transport` and `endpoint` must not be provided together
    if (config.transport && trackerConfig.endpoint) {
      throw new Error('Please provider either `transport` or `endpoint`, not both at same time');
    }

    // Automatically create a default Transport for the given `endpoint` with a sensible setup
    if (trackerConfig.endpoint) {
      config = {
        ...config,
        transport: makeBrowserTrackerDefaultTransport(config),
        queue: config.queue ?? makeBrowserTrackerDefaultQueue(config),
      };
    }

    // Configure to use provided `plugins` or automatically create a Plugins instance with some sensible web defaults
    if (isPluginsArray(trackerConfig.plugins) || trackerConfig.plugins === undefined) {
      const customPlugins = isPluginsArray(trackerConfig.plugins) ? trackerConfig.plugins : [];
      config.plugins = [...makeBrowserTrackerDefaultPluginsList(trackerConfig), ...customPlugins];
    } else {
      config.plugins = trackerConfig.plugins;
    }

    // Initialize core Tracker
    super(config, ...contextConfigs);

    // Store original config for comparison with other instances of Browser Tracker
    this.trackerConfig = trackerConfig;
  }
}
