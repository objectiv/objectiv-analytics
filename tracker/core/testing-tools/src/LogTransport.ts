/*
 * Copyright 2021 Objectiv B.V.
 */

import { TrackerConsole, TrackerTransportConfig, TrackerTransportInterface } from '@objectiv/tracker-core';

export class LogTransport implements TrackerTransportInterface {
  readonly console?: TrackerConsole;
  readonly transportName = 'LogTransport';

  constructor(config?: TrackerTransportConfig) {
    this.console = config?.console;
  }

  async handle(): Promise<any> {
    this.console?.log('LogTransport.handle');
  }

  isUsable(): boolean {
    return true;
  }
}
