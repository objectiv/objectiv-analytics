import { DebugTransport } from '../src/DebugTransport';
import { TrackerEvent } from '@objectiv/tracker-core';

describe('DebugTransport', () => {
  const testEvent = new TrackerEvent({
    event: 'test-event',
  });

  it('should `console.debug` the event', async () => {
    const testTransport = new DebugTransport();
    expect(testTransport.isUsable()).toBe(true);
    spyOn(console, 'debug');
    await testTransport.handle(testEvent);
    expect(console.debug).toHaveBeenCalledWith([testEvent]);
  });
});
