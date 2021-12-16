/*
 * Copyright 2021 Objectiv B.V.
 */

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
import { ReactTrackerConfig } from '../ReactTracker';

/**
 * The default XMLHttpRequest function implementation.
 */
export const defaultXMLHttpRequestFunction = ({
  endpoint,
  events,
  console,
}: {
  endpoint: string;
  events: [TrackerEvent, ...TrackerEvent[]];
  console?: TrackerConsole;
}): Promise<unknown> => {
  return new Promise(function (resolve, reject) {
    if (console) {
      console.groupCollapsed(`｢objectiv:XMLHttpRequestTransport｣ Sending`);
      console.log(`Events:`);
      console.log(events);
      console.groupEnd();
    }

    const xhr = new XMLHttpRequest();
    const async = true;
    xhr.open('POST', endpoint, async);
    xhr.setRequestHeader('Content-Type', 'text/plain');
    xhr.withCredentials = true;
    xhr.onload = () => {
      if (xhr.status === 200) {
        if (console) {
          console.groupCollapsed(`｢objectiv:XMLHttpRequestTransport｣ Succeeded`);
          console.log(`Events:`);
          console.log(events);
          console.groupEnd();
        }

        resolve(xhr.response);
      } else {
        if (console) {
          console.groupCollapsed(`｢objectiv:XMLHttpRequestTransport｣ Failed`);
          console.log(`Events:`);
          console.log(events);
          console.log(`Response: ${xhr}`);
          console.groupEnd();
        }

        reject(new TransportSendError());
      }
    };
    xhr.onerror = () => {
      if (console) {
        console.groupCollapsed(`｢objectiv:XMLHttpRequestTransport｣ Error`);
        console.log(`Events:`);
        console.log(events);
        console.groupEnd();
      }

      reject(new TransportSendError());
    };
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
export type XMLHttpRequestTransportConfig = TrackerTransportConfig &
  Pick<ReactTrackerConfig, 'endpoint'> & {
    /**
     * Optional. Override the default XMLHttpRequestFunction implementation with a custom one.
     */
    xmlHttpRequestFunction?: typeof defaultXMLHttpRequestFunction;
  };

/**
 * A TrackerTransport based on XMLHttpRequest. Sends event to the specified Collector endpoint.
 * Optionally supports specifying a custom `xmlHttpRequestFunction`.
 */
export class XMLHttpRequestTransport implements TrackerTransportInterface {
  readonly console?: TrackerConsole;
  readonly endpoint?: string;
  readonly transportName = 'XMLHttpRequestTransport';
  readonly xmlHttpRequestFunction: typeof defaultXMLHttpRequestFunction;

  constructor(config: XMLHttpRequestTransportConfig) {
    this.console = config.console;
    this.endpoint = config.endpoint;
    this.xmlHttpRequestFunction = config.xmlHttpRequestFunction ?? defaultXMLHttpRequestFunction;
  }

  async handle(...args: NonEmptyArray<TransportableEvent>): Promise<any> {
    const events = await Promise.all(args);

    if (this.endpoint && isNonEmptyArray(events)) {
      return this.xmlHttpRequestFunction({ endpoint: this.endpoint, console: this.console, events });
    }
  }

  isUsable(): boolean {
    return typeof XMLHttpRequest !== 'undefined';
  }
}
