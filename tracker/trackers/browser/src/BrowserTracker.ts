/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { ContextsConfig, isPluginsArray, Tracker, TrackerConfig, TrackerPlatform } from '@objectiv/tracker-core';
import { makeBrowserTrackerDefaultPluginsList } from './common/factories/makeBrowserTrackerDefaultPluginsList';
import { makeBrowserTrackerDefaultQueue } from './common/factories/makeBrowserTrackerDefaultQueue';
import { makeBrowserTrackerDefaultTransport } from './common/factories/makeBrowserTrackerDefaultTransport';
import { BrowserTrackerConfig } from './definitions/BrowserTrackerConfig';

/**
 * Browser Tracker is a Tracker Core constructor with simplified parameters and some preconfigured Plugins.
 * It initializes with a Queued Fetch and XMLHttpRequest Transport Switch wrapped in a Retry Transport automatically.
 * The resulting Queue has some sensible defaults (10 events every 100ms) for sending events in batches.
 * The Retry logic is configured for 10 retries with exponential backoff starting at 1000ms.
 *
 * This statement:
 *
 *  const tracker = new BrowserTracker({ applicationId: 'app-id', endpoint: '/endpoint' });
 *
 * is equivalent to:
 *
 *  const trackerId = trackerConfig.trackerId ?? trackerConfig.applicationId;
 *  const fetchTransport = new FetchTransport({ endpoint: '/endpoint' });
 *  const xhrTransport = new XHRTransport({ endpoint: '/endpoint' });
 *  const transportSwitch = new TransportSwitch({ transports: [fetchTransport, xhrTransport] });
 *  const transport = new RetryTransport({ transport: transportSwitch });
 *  const queueStorage = new LocalStorageQueueStore({ trackerId })
 *  const trackerQueue = new TrackerQueue({ storage: trackerStorage });
 *  const applicationContextPlugin = new ApplicationContextPlugin({ applicationId: 'app-id' });
 *  const httpContextPlugin = new HttpContextPlugin();
 *  const pathContextFromURLPlugin = new PathContextFromURLPlugin();
 *  const rootLocationContextFromURLPlugin = new RootLocationContextFromURLPlugin();
 *  const plugins = [
 *    applicationContextPlugin,
 *    httpContextPlugin,
 *    pathContextFromURLPlugin,
 *    rootLocationContextFromURLPlugin
 *  ];
 *  const tracker = new Tracker({ transport, queue, plugins });
 *
 *  @see makeBrowserTrackerDefaultPluginsList
 *  @see makeBrowserTrackerDefaultQueue
 *  @see makeBrowserTrackerDefaultTransport
 */
export class BrowserTracker extends Tracker {
  // A copy of the original configuration
  readonly trackerConfig: TrackerConfig;

  constructor(trackerConfig: BrowserTrackerConfig, ...contextConfigs: ContextsConfig[]) {
    let config: TrackerConfig = trackerConfig;

    // Set the platform
    config.platform = TrackerPlatform.BROWSER;

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
      config.plugins = [...makeBrowserTrackerDefaultPluginsList(trackerConfig), ...(trackerConfig.plugins ?? [])];
    } else {
      config.plugins = trackerConfig.plugins;
    }

    // Initialize core Tracker
    super(config, ...contextConfigs);

    // Store original config for comparison with other instances of Browser Tracker
    this.trackerConfig = trackerConfig;
  }
}
