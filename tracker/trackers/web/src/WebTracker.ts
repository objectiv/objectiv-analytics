import {
  MemoryQueue,
  QueuedTransport,
  Tracker,
  TrackerConfig,
  TrackerPlugins,
  TransportGroup,
  TransportSwitch,
} from '@objectiv/tracker-core';
import { FetchAPITransport } from './FetchAPITransport';
import { WebDocumentContextPlugin } from '@objectiv/plugin-web-document-context';
import { WebDeviceContextPlugin } from '@objectiv/plugin-web-device-context';
import { DebugTransport } from './DebugTransport';
import { XMLHttpRequestTransport } from './XMLHttpRequestTransport';

/**
 * Web Tracker can be configured in a easier way by specifying just an `endpoint`.
 * Internally it will automatically configure the Transport layer for the given `endpoint` with sensible defaults.
 */
export type WebTrackerConfig = TrackerConfig & {
  endpoint?: string;
};

/**
 * Web Tracker is a 1:1 instance of Tracker with a simplified construction and some preconfigured Plugins.
 * It initializes with a Queued Beacon and Fetch APIs Transport Switch automatically.
 * The resulting Queue has some sensible defaults (10 events every 100ms) for sending events in batches.
 *
 * This construction:
 *
 *  const webTracker = new WebTracker({ endpoint: '/endpoint' })
 *
 * is equivalent to:
 *
 *  const plugins = new TrackerPlugins([ WebDocumentContextPlugin, WebDeviceContextPlugin ]);
 *  const fetchTransport = new FetchAPITransport({ endpoint: '/endpoint' });
 *  const beaconTransport = new BeaconAPITransport({ endpoint: '/endpoint' });
 *  const debugTransport = new DebugTransport();
 *  const memoryQueue = new MemoryQueue();
 *  const transportSwitch = new TransportSwitch(beaconTransport, fetchTransport);
 *  const transportGroup = new TransportGroup(transportSwitch, debugTransport);
 *  const transport = new QueuedTransport({ transport: transportGroup, queue: memoryQueue });
 *  const tracker = new Tracker({ transport, plugins });
 *
 */
export class WebTracker extends Tracker {
  constructor(webConfig: WebTrackerConfig) {
    let config = webConfig;

    // Either `transport` or `endpoint` must be provided
    if (!config.transport && !config.endpoint) {
      throw new Error('Either `transport` or `endpoint` must be provided');
    }

    // `transport` and `endpoint` must not be provided together
    if (config.transport && config.endpoint) {
      throw new Error('Please provider either `transport` or `endpoint`, not both at same time');
    }

    // Automatically create a Memory Queued Beacon and Fetch APIs Transport Switch for the given `endpoint`
    if (config.endpoint) {
      config = {
        ...config,
        transport: new QueuedTransport({
          queue: new MemoryQueue(),
          transport: new TransportGroup(
            new TransportSwitch(
              new FetchAPITransport({ endpoint: config.endpoint }),
              new XMLHttpRequestTransport({ endpoint: config.endpoint })
            ),
            new DebugTransport()
          ),
        }),
      };
    }

    // Configure to use provided `plugins` or automatically create a Plugins instance with some sensible web defaults
    if (!config.plugins) {
      config = {
        ...config,
        plugins: new TrackerPlugins([WebDocumentContextPlugin, WebDeviceContextPlugin]),
      };
    }

    super(config);
  }
}
