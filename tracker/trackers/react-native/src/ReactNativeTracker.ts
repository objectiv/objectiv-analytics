/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { ContextsConfig, isPluginsArray, Tracker, TrackerConfig, TrackerPlatform } from '@objectiv/tracker-core';
import { makeReactNativeTrackerDefaultPluginsList } from './common/factories/makeReactNativeTrackerDefaultPluginsList';
import { makeReactNativeTrackerDefaultQueue } from './common/factories/makeReactNativeTrackerDefaultQueue';
import { makeReactNativeTrackerDefaultTransport } from './common/factories/makeReactNativeTrackerDefaultTransport';

/**
 * React Native Tracker can be configured in an easier way, as opposed to the core tracker.
 * The minimum required parameters are the `applicationId` and either an `endpoint` or a `transport` object.
 */
export type ReactNativeTrackerConfig = Omit<TrackerConfig, 'platform'> & {
  /**
   * The collector endpoint URL.
   */
  endpoint?: string;

  /**
   * Optional. Whether to track ApplicationContext automatically. Enabled by default.
   */
  trackApplicationContext?: boolean;
};

/**
 * React Native Tracker simplifies Tracker construction and adds some preconfigured Transport, Queue and Plugins.
 * It initializes with a Queued Fetch Transport wrapped in a Retry Transport.
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
 *  const transport = new RetryTransport({ transport: transportSwitch });
 *  const queueStorage = new TrackerQueueMemoryStorage({ trackerId })
 *  const trackerQueue = new TrackerQueue({ storage: queueStorage });
 *  const applicationContextPlugin = new ApplicationContextPlugin({ applicationId: 'app-id' });
 *  const plugins = [
 *    applicationContextPlugin,
 *  ];
 *  const tracker = new Tracker({ transport, queue, plugins });
 *
 *  @see makeReactNativeTrackerDefaultTransport
 *  @see makeReactNativeTrackerDefaultQueue
 *  @see makeReactNativeTrackerDefaultPluginsList
 */
export class ReactNativeTracker extends Tracker {
  constructor(trackerConfig: ReactNativeTrackerConfig, ...contextConfigs: ContextsConfig[]) {
    let config: TrackerConfig = trackerConfig;

    // Set the platform
    config.platform = TrackerPlatform.REACT_NATIVE;

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
        transport: makeReactNativeTrackerDefaultTransport(config),
        queue: config.queue ?? makeReactNativeTrackerDefaultQueue(),
      };
    }

    // Configure to use provided `plugins` or automatically create a Plugins instance with some sensible web defaults
    if (isPluginsArray(trackerConfig.plugins) || trackerConfig.plugins === undefined) {
      config.plugins = [...makeReactNativeTrackerDefaultPluginsList(trackerConfig), ...(trackerConfig.plugins ?? [])];
    } else {
      config.plugins = trackerConfig.plugins;
    }

    // Initialize Core Tracker
    super(config, ...contextConfigs);
  }
}
