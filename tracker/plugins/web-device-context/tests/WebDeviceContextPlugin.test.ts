import { WebDeviceContextPlugin } from '../src';
import { ContextsConfig, Tracker, TrackerEvent, TrackerPlugins } from '@objectiv/tracker-core';
import { clear, mockUserAgent } from 'jest-useragent-mock';

const USER_AGENT_MOCK_VALUE = 'Mocked User Agent';

describe('WebDeviceContextPlugin', () => {
  beforeEach(() => {
    mockUserAgent(USER_AGENT_MOCK_VALUE);
  });

  afterEach(() => {
    clear();
  });

  it('should generate a DeviceContext when constructed', () => {
    const testWebDeviceContextPlugin = new WebDeviceContextPlugin();
    expect(testWebDeviceContextPlugin.webDeviceContext).toEqual({
      __global_context: true,
      _context_type: 'DeviceContext',
      id: 'device',
      'user-agent': USER_AGENT_MOCK_VALUE,
    });
  });

  it('should add the DeviceContext to the Event when `beforeTransport` is executed by the Tracker', () => {
    const testTracker = new Tracker({ plugins: new TrackerPlugins([WebDeviceContextPlugin]) });
    const eventContexts: ContextsConfig = {
      global_contexts: [
        { __global_context: true, _context_type: 'section', id: 'X' },
        { __global_context: true, _context_type: 'section', id: 'Y' },
      ],
    };
    const testEvent = new TrackerEvent({ event: 'test-event', ...eventContexts });
    expect(testEvent.global_contexts).toHaveLength(2);
    const trackedEvent = testTracker.trackEvent(testEvent);
    expect(trackedEvent.global_contexts).toHaveLength(3);
    expect(trackedEvent.global_contexts).toEqual(
      expect.arrayContaining([
        {
          __global_context: true,
          _context_type: 'DeviceContext',
          id: 'device',
          'user-agent': USER_AGENT_MOCK_VALUE,
        },
      ])
    );
  });
});
