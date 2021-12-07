/*
 * Copyright 2021 Objectiv B.V.
 */

import { TrackerEvent } from '@objectiv/tracker-core';
import { DebugTransport } from '../src/';
import { mockConsole } from './mocks/MockConsole';

describe('DebugTransport', () => {
  const testEvent = new TrackerEvent({
    _type: 'test-event',
  });

  it('should `console.debug` the event', async () => {
    expect(mockConsole.debug).not.toHaveBeenCalled();
    const testTransport = new DebugTransport();
    const testTransportWithConsole = new DebugTransport({ console: mockConsole });
    expect(testTransport.isUsable()).toBe(true);
    expect(testTransportWithConsole.isUsable()).toBe(true);
    jest.spyOn(mockConsole, 'debug');
    await testTransport.handle(testEvent);
    await testTransportWithConsole.handle(testEvent);
    expect(mockConsole.debug).toHaveBeenCalledWith(testEvent);
  });
});
