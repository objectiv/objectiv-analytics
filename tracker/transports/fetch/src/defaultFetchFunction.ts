/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { TrackerEvent, makeTransportSendError } from '@objectiv/tracker-core';
import { defaultFetchOptions } from './defaultFetchOptions';

/**
 * The default fetch function implementation.
 */
export const defaultFetchFunction = async ({
  endpoint,
  events,
  options = defaultFetchOptions,
}: {
  endpoint: string;
  events: [TrackerEvent, ...TrackerEvent[]];
  options?: typeof defaultFetchOptions;
}): Promise<Response> => {
  return new Promise(function (resolve, reject) {
    if (globalThis.objectiv) {
      globalThis.objectiv.TrackerConsole.groupCollapsed(`｢objectiv:FetchTransport｣ Sending`);
      globalThis.objectiv.TrackerConsole.log(`Events:`);
      globalThis.objectiv.TrackerConsole.log(events);
      globalThis.objectiv.TrackerConsole.groupEnd();
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
          if (globalThis.objectiv) {
            globalThis.objectiv.TrackerConsole.groupCollapsed(`｢objectiv:FetchTransport｣ Succeeded`);
            globalThis.objectiv.TrackerConsole.log(`Events:`);
            globalThis.objectiv.TrackerConsole.log(events);
            globalThis.objectiv.TrackerConsole.groupEnd();
          }

          resolve(response);
        } else {
          if (globalThis.objectiv) {
            globalThis.objectiv.TrackerConsole.groupCollapsed(`｢objectiv:FetchTransport｣ Failed`);
            globalThis.objectiv.TrackerConsole.log(`Events:`);
            globalThis.objectiv.TrackerConsole.log(events);
            globalThis.objectiv.TrackerConsole.log(`Response: ${response}`);
            globalThis.objectiv.TrackerConsole.groupEnd();
          }

          reject(makeTransportSendError());
        }
      })
      .catch(() => {
        if (globalThis.objectiv) {
          globalThis.objectiv.TrackerConsole.groupCollapsed(`｢objectiv:FetchTransport｣ Error`);
          globalThis.objectiv.TrackerConsole.log(`Events:`);
          globalThis.objectiv.TrackerConsole.log(events);
          globalThis.objectiv.TrackerConsole.groupEnd();
        }

        reject(makeTransportSendError());
      });
  });
};
