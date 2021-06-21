import { TrackerEvent, TrackerTransport } from '@objectiv/tracker-core';

/**
 * A TrackerTransport that simply logs TrackerEvents to the console as debug messages.
 */
export class DebugTransport implements TrackerTransport {
  readonly transportName = 'DebugTransport';
  handle(...args: [TrackerEvent, ...TrackerEvent[]]): void {
    // We stringify and re-parse the TrackerEvent for our custom serializer to clean up discriminatory properties
    args.forEach((trackerEvent) => console.debug(JSON.parse(JSON.stringify(trackerEvent))));
  }

  isUsable(): boolean {
    return Boolean(console);
  }
}
