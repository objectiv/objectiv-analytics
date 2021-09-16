import { WebDeviceContextPlugin } from '../src';
import { ContextsConfig, Tracker, TrackerEvent, TrackerPlugins } from '@objectiv/tracker-core';

const origin = global.navigator.userAgent;
const cleared = Symbol('clear');
let fakeUserAgent: string | null | Symbol = null;

const USER_AGENT_MOCK_VALUE = 'Mocked User Agent';

Object.defineProperty(global.navigator, 'userAgent', {
  get() {
    return fakeUserAgent === cleared ? origin : fakeUserAgent || '';
  },
});

export const clear = () => {
  fakeUserAgent = cleared;
};

export const mockUserAgent = (agent: string) => {
  fakeUserAgent = agent;
};

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
      _type: 'DeviceContext',
      id: 'device',
      user_agent: USER_AGENT_MOCK_VALUE,
    });
  });

  it('should add the DeviceContext to the Event when `beforeTransport` is executed by the Tracker', async () => {
    const testTracker = new Tracker({ applicationId: 'app-id', plugins: new TrackerPlugins([WebDeviceContextPlugin]) });
    const eventContexts: ContextsConfig = {
      global_contexts: [
        { __global_context: true, _type: 'section', id: 'X' },
        { __global_context: true, _type: 'section', id: 'Y' },
      ],
    };
    const testEvent = new TrackerEvent({ _type: 'test-event', ...eventContexts });
    expect(testEvent.global_contexts).toHaveLength(2);
    const trackedEvent = await testTracker.trackEvent(testEvent);
    expect(trackedEvent.global_contexts).toHaveLength(3);
    expect(trackedEvent.global_contexts).toEqual(
      expect.arrayContaining([
        {
          __global_context: true,
          _type: 'DeviceContext',
          id: 'device',
          user_agent: USER_AGENT_MOCK_VALUE,
        },
      ])
    );
  });
});
