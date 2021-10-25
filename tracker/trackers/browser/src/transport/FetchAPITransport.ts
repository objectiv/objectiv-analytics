import { BrowserTrackerConfig } from '@objectiv/tracker-browser';
import {
  isNonEmptyArray,
  NonEmptyArray,
  TrackerConsole,
  TrackerEvent,
  TrackerTransportConfig,
  TrackerTransportInterface,
  TransportableEvent,
  TransportSendError,
} from '@objectiv/tracker-core';

/**
 * The default set of parameters for the fetch API call.
 * The `body` parameter is internally managed and should not be overridden.
 */
export const defaultFetchParameters: Omit<RequestInit, 'body'> = {
  method: 'POST',
  mode: 'cors',
  headers: {
    'Content-Type': 'text/plain',
  },
  credentials: 'include',
};

/**
 * The default fetch function implementation.
 */
export const defaultFetchFunction = async ({
  endpoint,
  events,
  parameters = defaultFetchParameters,
  console,
}: {
  endpoint: string;
  events: [TrackerEvent, ...TrackerEvent[]];
  parameters?: typeof defaultFetchParameters;
  console?: TrackerConsole;
}): Promise<Response> => {
  return new Promise(function (resolve, reject) {
    if (console) {
      console.groupCollapsed(`｢objectiv:FetchAPITransport｣ Sending`);
      console.log(`Events:`);
      console.log(events);
      console.groupEnd();
    }

    fetch(endpoint, {
      ...parameters,
      body: JSON.stringify({
        events,
        // add current timestamp to the request, so the collector
        // may check if there's any clock offset between server and client
        transport_time: Date.now(),
      }),
    })
      .then((response) => {
        if (response.status === 200) {
          if (console) {
            console.groupCollapsed(`｢objectiv:FetchAPITransport｣ Succeeded`);
            console.log(`Events:`);
            console.log(events);
            console.groupEnd();
          }

          resolve(response);
        } else {
          if (console) {
            console.groupCollapsed(`｢objectiv:FetchAPITransport｣ Failed`);
            console.log(`Events:`);
            console.log(events);
            console.log(`Response: ${response}`);
            console.groupEnd();
          }

          reject(new TransportSendError());
        }
      })
      .catch(() => {
        if (console) {
          console.groupCollapsed(`｢objectiv:FetchAPITransport｣ Error`);
          console.log(`Events:`);
          console.log(events);
          console.groupEnd();
        }

        reject(new TransportSendError());
      });
  });
};

/**
 * The configuration of the FetchAPITransport class
 */
export type FetchAPITransportConfig = TrackerTransportConfig &
  Pick<BrowserTrackerConfig, 'endpoint'> & {
    /**
     * Optional. Override the default fetch API implementation with a custom one.
     */
    fetchFunction?: typeof defaultFetchFunction;
  };

/**
 * A TrackerTransport based on Fetch API. Sends event to the specified Collector endpoint.
 * Optionally supports specifying a custom `fetchFunction`.
 */
export class FetchAPITransport implements TrackerTransportInterface {
  readonly console?: TrackerConsole;
  readonly endpoint?: string;
  readonly transportName = 'FetchAPITransport';
  readonly fetchFunction: typeof defaultFetchFunction;

  constructor(config: FetchAPITransportConfig) {
    this.console = config.console;
    this.endpoint = config.endpoint;
    this.fetchFunction = config.fetchFunction ?? defaultFetchFunction;
  }

  async handle(...args: NonEmptyArray<TransportableEvent>): Promise<Response | void> {
    const events = await Promise.all(args);

    if (this.endpoint && isNonEmptyArray(events)) {
      return this.fetchFunction({ endpoint: this.endpoint, console: this.console, events });
    }
  }

  isUsable(): boolean {
    return typeof fetch !== 'undefined';
  }
}
