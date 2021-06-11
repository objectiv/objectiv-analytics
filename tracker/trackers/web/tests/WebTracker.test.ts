import { defaultFetchFunction, FetchAPITransport, WebTracker } from '../src';
import { QueuedTransport, TrackerEvent, TrackerPlugins } from '@objectiv/tracker-core';
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
    expect(testTracker.transport).toBeInstanceOf(QueuedTransport);
    expect(testTracker.transport).toEqual({
      transportName: 'QueuedTransport',
      queue: {
        queueName: 'MemoryQueue',
        batchDelayMs: 250,
        batchSize: 10,
        events: [],
      },
      transport: {
        transportName: 'TransportGroup',
        usableTransports: [
          {
            transportName: 'TransportSwitch',
            firstUsableTransport: {
              transportName: 'FetchAPITransport',
              endpoint: 'localhost',
              fetchFunction: defaultFetchFunction,
            },
          },
          {
            transportName: 'DebugTransport',
          },
        ],
      },
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

    it('should track WebDocument and WebDevice Contexts as GlobalContexts automatically by default', () => {
      const testTracker = new WebTracker({ endpoint: 'localhost' });
      const testEvent = new TrackerEvent({ event: 'test-event' });
      expect(testTracker).toBeInstanceOf(WebTracker);
      expect(testEvent.globalContexts).toHaveLength(0);
      expect(testEvent.locationStack).toHaveLength(0);

      const trackedEvent = testTracker.trackEvent(testEvent);

      expect(trackedEvent.locationStack).toHaveLength(1);
      expect(trackedEvent.locationStack).toEqual(
        expect.arrayContaining([
          {
            _location_context: true,
            _section_context: true,
            _context_type: 'WebDocumentContext',
            id: '#document',
            url: 'http://localhost/',
          },
        ])
      );

      expect(trackedEvent.globalContexts).toHaveLength(1);
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
});
