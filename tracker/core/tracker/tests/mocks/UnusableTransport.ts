import { TrackerConsole, TrackerTransportConfig, TrackerTransportInterface } from '../../src';

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
