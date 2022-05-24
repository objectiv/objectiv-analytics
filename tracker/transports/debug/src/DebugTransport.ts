/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { NonEmptyArray, TrackerTransportInterface, TransportableEvent } from '@objectiv/tracker-core';

/**
 * A TrackerTransport that simply logs TrackerEvents to the console as debug messages.
 */
export class DebugTransport implements TrackerTransportInterface {
  readonly transportName = 'DebugTransport';

  async handle(...args: NonEmptyArray<TransportableEvent>): Promise<any> {
    // We stringify and re-parse the TrackerEvent for our custom serializer to clean up discriminatory properties
    (await Promise.all(args)).forEach((trackerEvent) => console.debug(JSON.parse(JSON.stringify(trackerEvent))));
  }

  isUsable(): boolean {
    return Boolean(console);
  }
}
