import { TrackerTransport } from '../../src';

export class LogTransport implements TrackerTransport {
  readonly transportName = 'LogTransport';
  handle(): void {
    console.log('LogTransport.handle');
  }

  isUsable(): boolean {
    return true;
  }
}
