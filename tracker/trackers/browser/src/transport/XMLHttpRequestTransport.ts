import {
  isNonEmptyArray,
  NonEmptyArray,
  TrackerEvent,
  TrackerTransport,
  TransportableEvent,
  TransportSendError,
} from '@objectiv/tracker-core';

/**
 * The default XMLHttpRequest function implementation.
 */
export const defaultXMLHttpRequestFunction = ({
  endpoint,
  events,
}: {
  endpoint: string;
  events: [TrackerEvent, ...TrackerEvent[]];
}): Promise<unknown> => {
  return new Promise(function (resolve, reject) {
    const xhr = new XMLHttpRequest();
    const async = true;
    xhr.open('POST', endpoint, async);
    xhr.setRequestHeader('Content-Type', 'text/plain');
    xhr.withCredentials = true;
    xhr.onload = () => {
      if (xhr.status === 200) {
        resolve(xhr.response);
      } else {
        reject(new TransportSendError());
      }
    };
    xhr.onerror = () => reject(new TransportSendError());
    xhr.send(
      JSON.stringify({
        events,
        // add current timestamp to the request, so the collector
        // may check if there's any clock offset between server and client
        transport_time: Date.now(),
      })
    );
  });
};

/**
 * The configuration of the XMLHttpRequestTransport class
 */
export type XMLHttpRequestTransportConfig = {
  /**
   * Collector's URI. Where to send the Events to.
   */
  endpoint: string;

  /**
   * Optional. Override the default XMLHttpRequestFunction implementation with a custom one.
   */
  xmlHttpRequestFunction?: typeof defaultXMLHttpRequestFunction;
};

/**
 * A TrackerTransport based on XMLHttpRequest. Sends event to the specified Collector endpoint.
 * Optionally supports specifying a custom `xmlHttpRequestFunction`.
 */
export class XMLHttpRequestTransport implements TrackerTransport {
  readonly transportName = 'XMLHttpRequestTransport';
  readonly endpoint: string;
  readonly xmlHttpRequestFunction: typeof defaultXMLHttpRequestFunction;

  constructor(config: XMLHttpRequestTransportConfig) {
    this.endpoint = config.endpoint;
    this.xmlHttpRequestFunction = config.xmlHttpRequestFunction ?? defaultXMLHttpRequestFunction;
  }

  async handle(...args: NonEmptyArray<TransportableEvent>): Promise<any> {
    const events = await Promise.all(args);
    if (isNonEmptyArray(events)) {
      return this.xmlHttpRequestFunction({ endpoint: this.endpoint, events });
    }
  }

  isUsable(): boolean {
    return typeof XMLHttpRequest !== 'undefined';
  }
}
