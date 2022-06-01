/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { TrackerTransportInterface } from '@objectiv/tracker-core';

export class UnusableTransport implements TrackerTransportInterface {
  readonly transportName = 'UnusableTransport';

  async handle(): Promise<any> {
    globalThis.objectiv?.TrackerConsole.log('UnusableTransport.handle');
  }

  isUsable(): boolean {
    return false;
  }
}
