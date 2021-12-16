/*
 * Copyright 2021 Objectiv B.V.
 */

import {
  NonEmptyArray,
  TrackerConsole,
  TrackerTransportConfig,
  TrackerTransportInterface,
  TransportableEvent,
} from '@objectiv/tracker-core';

/**
 * A TrackerTransport that simply logs TrackerEvents to the console as debug messages.
 */
export class DebugTransport implements TrackerTransportInterface {
  readonly console?: TrackerConsole;
  readonly transportName = 'DebugTransport';

  constructor(config?: TrackerTransportConfig) {
    this.console = config?.console;
  }

  async handle(...args: NonEmptyArray<TransportableEvent>): Promise<any> {
    // We stringify and re-parse the TrackerEvent for our custom serializer to clean up discriminatory properties
    (await Promise.all(args)).forEach((trackerEvent) => this.console?.debug(JSON.parse(JSON.stringify(trackerEvent))));
  }

  isUsable(): boolean {
    return Boolean(console);
  }
}
