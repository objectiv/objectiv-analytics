/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { NonEmptyArray } from './helpers';
import { TrackerTransportInterface, TransportableEvent } from './TrackerTransportInterface';

/**
 * The configuration of TrackerTransportGroup.
 */
export type TransportGroupConfig = {
  transports: NonEmptyArray<TrackerTransportInterface>;
};

/**
 * TrackerTransportGroup provides a mechanism to hand over TrackerEvents to multiple transports. The group is usable
 * if at least one of the given TrackerTransports is usable.
 *
 * This can be used when having multiple Collectors but also for simpler development needs, such as handling & logging
 */
export class TrackerTransportGroup implements TrackerTransportInterface {
  readonly transportName = 'TrackerTransportGroup';
  readonly usableTransports: TrackerTransportInterface[];

  /**
   * Filter and store the list of usable transports, received as construction parameters, in state
   */
  constructor(config: TransportGroupConfig) {
    this.usableTransports = config.transports.filter((transport) => transport.isUsable());

    if (globalThis.objectiv.devTools) {
      globalThis.objectiv.devTools.TrackerConsole.groupCollapsed(`｢objectiv:${this.transportName}｣ Initialized`);
      globalThis.objectiv.devTools.TrackerConsole.log(
        `Transports: ${config.transports.map((transport) => transport.transportName).join(', ')}`
      );
      globalThis.objectiv.devTools.TrackerConsole.log(
        `Usable Transports: ${this.usableTransports.map((transport) => transport.transportName).join(', ')}`
      );
      globalThis.objectiv.devTools.TrackerConsole.groupEnd();
    }
  }

  /**
   * Simply proxy the `handle` method to all the usable TrackerTransport instances we have.
   */
  async handle(...args: NonEmptyArray<TransportableEvent>): Promise<any> {
    if (!this.usableTransports.length) {
      return Promise.reject(`${this.transportName}: no usable Transports found; make sure to verify usability first.`);
    }

    return this.usableTransports.map((transport) => transport.handle(...args));
  }

  /**
   * The whole TransportGroup is usable if we found at least one usable TrackerTransport
   */
  isUsable(): boolean {
    return Boolean(this.usableTransports.length);
  }
}
