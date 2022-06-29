/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { NonEmptyArray } from './helpers';
import { TrackerTransportInterface, TransportableEvent } from './TrackerTransportInterface';

/**
 * The configuration of TrackerTransportSwitch.
 */
export type TrackerTransportSwitchConfig = {
  transports: NonEmptyArray<TrackerTransportInterface>;
};

/**
 * TrackerTransportSwitch provides a fallback mechanism to pick the first usable transport in a list of them.
 * The switch is usable if at least one of the given TrackerTransports is usable.
 *
 * This mechanism can be used to configure multiple TrackerTransport instances, in order of preference, and
 * have TransportSwitch test each of them via the `isUsable` method to determine the topmost usable one.
 */
export class TrackerTransportSwitch implements TrackerTransportInterface {
  readonly transportName = 'TrackerTransportSwitch';
  readonly firstUsableTransport?: TrackerTransportInterface;

  /**
   * Finds the first TrackerTransport which `isUsable()`.
   */
  constructor(config: TrackerTransportSwitchConfig) {
    this.firstUsableTransport = config.transports.find((trackerTransport) => trackerTransport.isUsable());

    if (globalThis.objectiv.devTools) {
      globalThis.objectiv.devTools.TrackerConsole.groupCollapsed(`｢objectiv:${this.transportName}｣ Initialized`);
      globalThis.objectiv.devTools.TrackerConsole.log(
        `Transports: ${config.transports.map((transport) => transport.transportName).join(', ')}`
      );
      globalThis.objectiv.devTools.TrackerConsole.log(
        `First usable Transport: ${this.firstUsableTransport?.transportName ?? 'none'}`
      );
      globalThis.objectiv.devTools.TrackerConsole.groupEnd();
    }
  }

  /**
   * Simply proxy the `handle` method to the usable TrackerTransport we found during construction, if any
   */
  async handle(...args: NonEmptyArray<TransportableEvent>): Promise<any> {
    if (!this.firstUsableTransport) {
      return Promise.reject(`${this.transportName}: no usable Transport found; make sure to verify usability first.`);
    }

    return this.firstUsableTransport.handle(...args);
  }

  /**
   * The whole TransportSwitch is usable if we found a usable TrackerTransport
   */
  isUsable(): boolean {
    return Boolean(this.firstUsableTransport);
  }
}
