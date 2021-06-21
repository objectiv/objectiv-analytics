import { defaultFetchFunction, FetchAPITransport, TransportGroup, WebTracker } from '../src';
import { TrackerEvent, TrackerPlugins } from '@objectiv/tracker-core';
import fetchMock from 'jest-fetch-mock';
import { clear, mockUserAgent } from 'jest-useragent-mock';

describe('WebTracker', () => {
  it('should not instantiate without either `transport` or `endpoint`', () => {
    expect(() => new WebTracker({})).toThrow();
  });

  it('should not instantiate with both `endpoint` and `transport`', () => {
    expect(
      () =>
        new WebTracker({
          endpoint: 'localhost',
          transport: new FetchAPITransport({
            endpoint: 'localhost',
          }),
        })
    ).toThrow();
  });

  it('should instantiate with `endpoint`', () => {
    const testTracker = new WebTracker({ endpoint: 'localhost' });
    expect(testTracker).toBeInstanceOf(WebTracker);
    expect(testTracker.transport).toBeInstanceOf(TransportGroup);
    expect(testTracker.transport).toEqual({
      transportName: 'TransportGroup',
      usableTransports: [
        {
          transportName: 'QueuedTransport',
          queue: {
            queueName: 'MemoryQueue',
            batchDelayMs: 250,
            batchSize: 10,
            events: [],
          },
          transport: {
            transportName: 'TransportSwitch',
            firstUsableTransport: {
              transportName: 'FetchAPITransport',
              endpoint: 'localhost',
              fetchFunction: defaultFetchFunction,
            },
          },
        },
        {
          transportName: 'DebugTransport',
        },
      ],
    });
  });

  it('should instantiate with `transport`', () => {
    const testTracker = new WebTracker({ transport: new FetchAPITransport({ endpoint: 'localhost' }) });
    expect(testTracker).toBeInstanceOf(WebTracker);
    expect(testTracker.transport).toBeInstanceOf(FetchAPITransport);
  });

  describe('Default Plugins', () => {
    it('should have some Web Plugins configured by default when no `plugins` have been specified', () => {
      const testTracker = new WebTracker({ endpoint: 'localhost' });
      expect(testTracker).toBeInstanceOf(WebTracker);
      expect(testTracker.plugins?.list).toEqual(
        expect.arrayContaining([
          expect.objectContaining({ pluginName: 'WebDocumentContextPlugin' }),
          expect.objectContaining({ pluginName: 'WebDeviceContextPlugin' }),
        ])
      );
    });

    it('should not have any default Plugin configured when `plugins` have been overridden', () => {
      const testTracker = new WebTracker({ endpoint: 'localhost', plugins: new TrackerPlugins([]) });
      expect(testTracker).toBeInstanceOf(WebTracker);
      expect(testTracker.plugins?.list).toStrictEqual([]);
    });
  });

  describe('trackEvent', () => {
    const USER_AGENT_MOCK_VALUE = 'Mocked User Agent';

    beforeEach(() => {
      fetchMock.enableMocks();
      mockUserAgent(USER_AGENT_MOCK_VALUE);
    });

    afterEach(() => {
      fetchMock.resetMocks();
      clear();
    });

    it('should track WebDocument and WebDevice Contexts as global_contexts automatically by default', () => {
      const testTracker = new WebTracker({ endpoint: 'localhost' });
      const testEvent = new TrackerEvent({ event: 'test-event' });
      expect(testTracker).toBeInstanceOf(WebTracker);
      expect(testEvent.global_contexts).toHaveLength(0);
      expect(testEvent.location_stack).toHaveLength(0);

      const trackedEvent = testTracker.trackEvent(testEvent);

      expect(trackedEvent.location_stack).toHaveLength(1);
      expect(trackedEvent.location_stack).toEqual(
        expect.arrayContaining([
          {
            _context_type: 'WebDocumentContext',
            id: '#document',
            url: 'http://localhost/',
          },
        ])
      );

      expect(trackedEvent.global_contexts).toHaveLength(1);
      expect(trackedEvent.global_contexts).toEqual(
        expect.arrayContaining([
          {
            _context_type: 'DeviceContext',
            id: 'device',
            'user-agent': USER_AGENT_MOCK_VALUE,
          },
        ])
      );
    });
  });
});
