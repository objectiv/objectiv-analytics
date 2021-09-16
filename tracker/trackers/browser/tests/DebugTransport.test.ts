import { TrackerEvent } from '@objectiv/tracker-core';
import { DebugTransport } from '../src/';

describe('DebugTransport', () => {
  const testEvent = new TrackerEvent({
    _type: 'test-event',
  });

  it('should `console.debug` the event', async () => {
    const testTransport = new DebugTransport();
    expect(testTransport.isUsable()).toBe(true);
    jest.spyOn(console, 'debug');
    await testTransport.handle(testEvent);
    expect(console.debug).toHaveBeenCalledWith(testEvent);
  });
});
