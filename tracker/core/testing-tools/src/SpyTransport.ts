/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { TrackerTransportInterface } from '@objectiv/tracker-core';

export class SpyTransport implements TrackerTransportInterface {
  readonly transportName = 'SpyTransport';

  async handle(): Promise<any> {
    globalThis.objectiv?.TrackerConsole.log('SpyTransport.handle');
  }

  isUsable(): boolean {
    return true;
  }
}
