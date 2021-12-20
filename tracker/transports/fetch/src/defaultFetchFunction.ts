/*
 * Copyright 2021 Objectiv B.V.
 */

import { TrackerConsole, TrackerEvent, TransportSendError } from '@objectiv/tracker-core';
import { defaultFetchOptions } from './defaultFetchOptions';

/**
 * The default fetch function implementation.
 */
export const defaultFetchFunction = async ({
  endpoint,
  events,
  options = defaultFetchOptions,
  console,
}: {
  endpoint: string;
  events: [TrackerEvent, ...TrackerEvent[]];
  options?: typeof defaultFetchOptions;
  console?: TrackerConsole;
}): Promise<Response> => {
  return new Promise(function (resolve, reject) {
    if (console) {
      console.groupCollapsed(`｢objectiv:FetchTransport｣ Sending`);
      console.log(`Events:`);
      console.log(events);
      console.groupEnd();
    }

    fetch(endpoint, {
      ...options,
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
            console.groupCollapsed(`｢objectiv:FetchTransport｣ Succeeded`);
            console.log(`Events:`);
            console.log(events);
            console.groupEnd();
          }

          resolve(response);
        } else {
          if (console) {
            console.groupCollapsed(`｢objectiv:FetchTransport｣ Failed`);
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
          console.groupCollapsed(`｢objectiv:FetchTransport｣ Error`);
          console.log(`Events:`);
          console.log(events);
          console.groupEnd();
        }

        reject(new TransportSendError());
      });
  });
};
