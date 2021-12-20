/*
 * Copyright 2021 Objectiv B.V.
 */

import {
  isNonEmptyArray,
  NonEmptyArray,
  TrackerConsole,
  TrackerTransportConfig,
  TrackerTransportInterface,
  TransportableEvent,
} from '@objectiv/tracker-core';
import { defaultFetchFunction } from './defaultFetchFunction';

/**
 * The configuration of the FetchTransport class
 */
export type FetchTransportConfig = TrackerTransportConfig & {
  /**
   * The collector endpoint URL.
   */
  endpoint?: string;

  /**
   * Optional. Override the default fetch API implementation with a custom one.
   */
  fetchFunction?: typeof defaultFetchFunction;
};

/**
 * A TrackerTransport based on Fetch API. Sends event to the specified Collector endpoint.
 * Optionally supports specifying a custom `fetchFunction`.
 */
export class FetchTransport implements TrackerTransportInterface {
  readonly console?: TrackerConsole;
  readonly endpoint?: string;
  readonly transportName = 'FetchTransport';
  readonly fetchFunction: typeof defaultFetchFunction;

  constructor(config: FetchTransportConfig) {
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
