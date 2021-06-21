import { TrackerTransport } from '@objectiv/tracker-core';

export class SpyTransport implements TrackerTransport {
  readonly transportName = 'SpyTransport';
  handle(): void {
    console.log('SpyTransport.handle');
  }
  isUsable(): boolean {
    return true;
  }
}
