/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { TrackerTransportInterface } from '@objectiv/tracker-core';

export class LogTransport implements TrackerTransportInterface {
  readonly transportName = 'LogTransport';

  async handle(): Promise<any> {
    globalThis.objectiv.devTools?.TrackerConsole.log('LogTransport.handle');
  }

  isUsable(): boolean {
    return true;
  }
}
