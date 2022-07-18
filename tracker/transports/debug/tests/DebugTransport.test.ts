/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { generateGUID, TrackerEvent } from '@objectiv/tracker-core';
import { DebugTransport } from '../src/';

describe('DebugTransport', () => {
  const testEvent = new TrackerEvent({
    _type: 'test-event',
    id: generateGUID(),
    time: Date.now(),
  });

  it('should `console.debug` the event', async () => {
    jest.spyOn(console, 'debug');
    expect(console.debug).not.toHaveBeenCalled();
    const testTransport = new DebugTransport();
    const testTransportWithConsole = new DebugTransport();
    expect(testTransport.isUsable()).toBe(true);
    expect(testTransportWithConsole.isUsable()).toBe(true);
    jest.spyOn(console, 'debug');
    await testTransport.handle(testEvent);
    await testTransportWithConsole.handle(testEvent);
    expect(console.debug).toHaveBeenCalledWith(testEvent);
  });
});
