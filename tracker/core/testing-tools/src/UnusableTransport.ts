/*
 * Copyright 2021 Objectiv B.V.
 */

import { TrackerConsole, TrackerTransportConfig } from '@objectiv/tracker-core';

import { TrackerTransportInterface } from '@objectiv/tracker-core';

export class UnusableTransport implements TrackerTransportInterface {
  readonly console?: TrackerConsole;
  readonly transportName = 'UnusableTransport';

  constructor(config?: TrackerTransportConfig) {
    this.console = config?.console;
  }

  async handle(): Promise<any> {
    this.console?.log('LogTransport.handle');
  }

  isUsable(): boolean {
    return false;
  }
}
