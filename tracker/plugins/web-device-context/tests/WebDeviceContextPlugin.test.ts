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
      _global_context: true,
      _context_type: 'DeviceContext',
      id: 'device',
      userAgent: USER_AGENT_MOCK_VALUE,
    });
  });

  it('should add the DeviceContext to the Event when `beforeTransport` is executed by the Tracker', () => {
    const testTracker = new Tracker({ plugins: new TrackerPlugins([WebDeviceContextPlugin]) });
    const eventContexts: ContextsConfig = {
      globalContexts: [
        { _global_context: true, _context_type: 'section', id: 'X' },
        { _global_context: true, _context_type: 'section', id: 'Y' },
      ],
    };
    const testEvent = new TrackerEvent({ event: 'test-event', ...eventContexts });
    expect(testEvent.globalContexts).toHaveLength(2);
    const trackedEvent = testTracker.trackEvent(testEvent);
    expect(trackedEvent.globalContexts).toHaveLength(3);
    expect(trackedEvent.globalContexts).toEqual(
      expect.arrayContaining([
        {
          _global_context: true,
          _context_type: 'DeviceContext',
          id: 'device',
          userAgent: USER_AGENT_MOCK_VALUE,
        },
      ])
    );
  });
});
