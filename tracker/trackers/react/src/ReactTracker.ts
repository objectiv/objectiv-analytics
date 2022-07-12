/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { ContextsConfig, isPluginsArray, Tracker, TrackerConfig, TrackerPlatform } from '@objectiv/tracker-core';
import { makeReactTrackerDefaultPluginsList } from './common/factories/makeReactTrackerDefaultPluginsList';
import { makeReactTrackerDefaultQueue } from './common/factories/makeReactTrackerDefaultQueue';
import { makeReactTrackerDefaultTransport } from './common/factories/makeReactTrackerDefaultTransport';

/**
 * React Tracker can be configured in an easier way, as opposed to the core tracker.
 * The minimum required parameters are the `applicationId` and either an `endpoint` or a `transport` object.
 */
export type ReactTrackerConfig = Omit<TrackerConfig, 'platform'> & {
  /**
   * The collector endpoint URL.
   */
  endpoint?: string;

  /**
   * Optional. Whether to track ApplicationContext automatically. Enabled by default.
   */
  trackApplicationContext?: boolean;

  /**
   * Optional. Whether to automatically create HttpContext based on Document and Navigation APIs. Enabled by default.
   */
  trackHttpContext?: boolean;

  /**
   * Optional. Whether to automatically create PathContext based on URLs. Enabled by default.
   */
  trackPathContextFromURL?: boolean;

  /**
   * Optional. Whether to automatically create RootLocationContext based on URLs first slugs. Enabled by default.
   */
  trackRootLocationContextFromURL?: boolean;
};

/**
 * React Tracker simplifies Tracker construction and adds some preconfigured Transport, Queue and Plugins.
 * It initializes with a Queued Fetch|XMLHttpRequest Transport Switch wrapped in a Retry Transport.
 *
 * The resulting Queue has some sensible defaults (10 events every 100ms) for sending events in batches.
 * The Retry logic is configured for 10 retries with exponential backoff starting at 1000ms.
 *
 * This statement:
 *
 *  const tracker = new ReactTracker({ applicationId: 'app-id', endpoint: '/endpoint' });
 *
 * is equivalent to:
 *
 *  const trackerId = trackerConfig.trackerId ?? trackerConfig.applicationId;
 *  const fetchTransport = new FetchAPITransport({ endpoint: '/endpoint' });
 *  const xmlHttpRequestTransport = new XMLHttpRequestTransport({ endpoint: '/endpoint' });
 *  const transportSwitch = new TransportSwitch({ transports: [fetchTransport, xmlHttpRequestTransport] });
 *  const transport = new RetryTransport({ transport: transportSwitch });
 *  const queueStorage = new TrackerQueueLocalStorage({ trackerId })
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
 *  @see makeReactTrackerDefaultTransport
 *  @see makeReactTrackerDefaultQueue
 *  @see makeReactTrackerDefaultPluginsList
 */
export class ReactTracker extends Tracker {
  constructor(trackerConfig: ReactTrackerConfig, ...contextConfigs: ContextsConfig[]) {
    let config: TrackerConfig = trackerConfig;

    // Set the platform
    config.platform = TrackerPlatform.REACT;

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
        transport: makeReactTrackerDefaultTransport(config),
        queue: config.queue ?? makeReactTrackerDefaultQueue(config),
      };
    }

    // Configure to use provided `plugins` or automatically create a Plugins instance with some sensible web defaults
    if (isPluginsArray(trackerConfig.plugins) || trackerConfig.plugins === undefined) {
      config.plugins = [...makeReactTrackerDefaultPluginsList(trackerConfig), ...(trackerConfig.plugins ?? [])];
    } else {
      config.plugins = trackerConfig.plugins;
    }

    // Initialize Core Tracker
    super(config, ...contextConfigs);
  }
}
