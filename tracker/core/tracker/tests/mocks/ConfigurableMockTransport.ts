import { TrackerConsole, TrackerTransportConfig, TrackerTransportInterface } from '../../src';

export class ConfigurableMockTransport implements TrackerTransportInterface {
  readonly console?: TrackerConsole;
  readonly transportName = 'ConfigurableMockTransport';
  _isUsable: boolean;

  constructor({ console, isUsable }: TrackerTransportConfig & { isUsable: boolean }) {
    this.console = console;
    this._isUsable = isUsable;
  }

  async handle(): Promise<any> {
    this.console?.log('MockTransport.handle');
  }

  isUsable(): boolean {
    return this._isUsable;
  }
}
