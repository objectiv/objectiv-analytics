/*
 * Copyright 2021 Objectiv B.V.
 */

import { TrackerConsole, TrackerTransportConfig, TrackerTransportInterface } from '@objectiv/tracker-core';

export class SpyTransport implements TrackerTransportInterface {
  readonly console?: TrackerConsole;
  readonly transportName = 'SpyTransport';

  constructor(config?: TrackerTransportConfig) {
    this.console = config?.console;
  }

  async handle(): Promise<any> {
    this.console?.log('SpyTransport.handle');
  }

  isUsable(): boolean {
    return true;
  }
}
