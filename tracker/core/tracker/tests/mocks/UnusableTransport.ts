import { TrackerTransport } from '../../src';

export class UnusableTransport implements TrackerTransport {
  readonly transportName = 'UnusableTransport';
  handle(): void {
    console.log('LogTransport.handle');
  }

  isUsable(): boolean {
    return false;
  }
}
