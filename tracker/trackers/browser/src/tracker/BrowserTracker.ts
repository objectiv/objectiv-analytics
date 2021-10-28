import { WebDeviceContextPlugin } from '@objectiv/plugin-web-device-context';
import { WebDocumentContextPlugin } from '@objectiv/plugin-web-document-context';
import {
  ContextsConfig,
  getDefaultTrackerPluginsList,
  Tracker,
  TrackerConfig,
  TrackerPlugins,
  TrackerQueue,
  TrackerQueueInterface,
  TrackerTransportInterface,
  TrackerTransportRetry,
  TrackerTransportSwitch,
} from '@objectiv/tracker-core';
import { FetchAPITransport } from '../transport/FetchAPITransport';
import { TrackerQueueLocalStorageStore } from '../transport/TrackerQueueLocalStorageStore';
import { XMLHttpRequestTransport } from '../transport/XMLHttpRequestTransport';

/**
 * Browser Tracker can be configured in a easier way, as opposed to the core tracker, by specifying just an `endpoint`.
 * Internally it will automatically configure the Transport layer for the given `endpoint` with sensible defaults.
 * It also accepts a number of options to configure automatic tracking behavior:
 */
export type BrowserTrackerConfig = TrackerConfig & {
  /**
   * The collector endpoint URL.
   */
  endpoint?: string;

  /**
   * Optional. Whether to track application loaded events automatically. Enabled by default.
   */
  trackApplicationLoaded?: boolean;

  /**
   * Optional. Whether to track URL change events automatically. Enabled by default.
   */
  trackURLChanges?: boolean;
};

/**
 * A factory to create the default Transport of Browser Tracker.
 */
export const makeBrowserTrackerDefaultTransport = (trackerConfig: BrowserTrackerConfig): TrackerTransportInterface =>
  new TrackerTransportRetry({
    console: trackerConfig.console,
    transport: new TrackerTransportSwitch({
      console: trackerConfig.console,
      transports: [
        new FetchAPITransport({ endpoint: trackerConfig.endpoint, console: trackerConfig.console }),
        new XMLHttpRequestTransport({ endpoint: trackerConfig.endpoint, console: trackerConfig.console }),
      ],
    }),
  });

/**
 * A factory to create the default Queue of Browser Tracker.
 */
export const makeBrowserTrackerDefaultQueue = (trackerConfig: BrowserTrackerConfig): TrackerQueueInterface =>
  new TrackerQueue({
    store: new TrackerQueueLocalStorageStore({
      trackerId: trackerConfig.trackerId ?? trackerConfig.applicationId,
      console: trackerConfig.console,
    }),
    console: trackerConfig.console,
  });

/**
 * The default list of Plugins of Browser Tracker
 */
export const getDefaultBrowserTrackerPluginsList = (trackerConfig: BrowserTrackerConfig) => [
  ...getDefaultTrackerPluginsList(trackerConfig),
  new WebDocumentContextPlugin({ console: trackerConfig.console }),
  new WebDeviceContextPlugin({ console: trackerConfig.console }),
];

/**
 * Browser Tracker is a 1:1 instance of Tracker core with a simplified construction and some preconfigured Plugins.
 * It initializes with a Queued Fetch and XMLHttpRequest Transport Switch wrapped in a Retry Transport automatically.
 * The resulting Queue has some sensible defaults (10 events every 100ms) for sending events in batches.
 * The Retry logic is configured for 10 retries with exponential backoff starting at 1000ms.
 *
 * This statement:
 *
 *  const tracker = new BrowserTracker({ applicationId: 'app-id', endpoint: '/endpoint', console: console });
 *
 * is equivalent to:
 *
 *  const trackerId = trackerConfig.trackerId ?? trackerConfig.applicationId;
 *  const console = trackerConfig.console;
 *  const fetchTransport = new FetchAPITransport({ endpoint: '/endpoint', console });
 *  const xmlHttpRequestTransport = new XMLHttpRequestTransport({ endpoint: '/endpoint', console });
 *  const transportSwitch = new TransportSwitch({ transports: [fetchTransport, xmlHttpRequestTransport], console });
 *  const transport = new RetryTransport({ transport: transportSwitch, console });
 *  const queueStorage = new TrackerQueueLocalStorageStore({ trackerId, console })
 *  const trackerQueue = new TrackerQueue({ storage: trackerStorage, console });
 *  const applicationContextPlugin = new ApplicationContextPlugin({ applicationId: 'app-id', console });
 *  const webDocumentContextPlugin = new WebDocumentContextPlugin({ console });
 *  const webDeviceContextPlugin = new WebDeviceContextPlugin({ console });
 *  const plugins = new TrackerPlugins({
 *    plugins: [ applicationContextPlugin, webDocumentContextPlugin, webDeviceContextPlugin ],
 *    console
 *  });
 *  const tracker = new Tracker({ transport, queue, plugins, console });
 *
 *  See also `makeBrowserTrackerDefaultTransport` and `makeBrowserTrackerDefaultQueue` for the actual implementation.
 *
 */
export class BrowserTracker extends Tracker {
  constructor(trackerConfig: BrowserTrackerConfig, ...contextConfigs: ContextsConfig[]) {
    let config = trackerConfig;

    // Either `transport` or `endpoint` must be provided
    if (!config.transport && !config.endpoint) {
      throw new Error('Either `transport` or `endpoint` must be provided');
    }

    // `transport` and `endpoint` must not be provided together
    if (config.transport && config.endpoint) {
      throw new Error('Please provider either `transport` or `endpoint`, not both at same time');
    }

    // If node is in `development` mode and console has not been configured, automatically use the browser's console
    if (!config.console && process.env.NODE_ENV?.startsWith('dev')) {
      config.console = console;
    }

    // Automatically create a default Transport for the given `endpoint` with a sensible setup
    if (config.endpoint) {
      config = {
        ...config,
        transport: makeBrowserTrackerDefaultTransport(config),
        queue: makeBrowserTrackerDefaultQueue(config),
      };
    }

    // Configure to use provided `plugins` or automatically create a Plugins instance with some sensible web defaults
    if (!config.plugins) {
      config = {
        ...config,
        plugins: new TrackerPlugins({
          console: trackerConfig.console,
          plugins: getDefaultBrowserTrackerPluginsList(config),
        }),
      };
    }

    // Initialize core Tracker
    super(config, ...contextConfigs);
  }
}
