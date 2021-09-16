import { TrackerEvent, TrackerPlugins, TransportGroup } from '@objectiv/tracker-core';
import fetchMock from 'jest-fetch-mock';
import { clear, mockUserAgent } from 'jest-useragent-mock';
import { BrowserTracker, defaultFetchFunction, FetchAPITransport } from '../src/';

describe('BrowserTracker', () => {
  it('should not instantiate without either `transport` or `endpoint`', () => {
    expect(
      () =>
        new BrowserTracker({
          applicationId: 'app-id',
        })
    ).toThrow();
  });

  it('should not instantiate with both `endpoint` and `transport`', () => {
    expect(
      () =>
        new BrowserTracker({
          applicationId: 'app-id',
          endpoint: 'localhost',
          transport: new FetchAPITransport({
            endpoint: 'localhost',
          }),
        })
    ).toThrow();
  });

  it('should instantiate with `applicationId` and `endpoint`', () => {
    const testTracker = new BrowserTracker({ applicationId: 'app-id', endpoint: 'localhost' });
    expect(testTracker).toBeInstanceOf(BrowserTracker);
    expect(testTracker.transport).toBeInstanceOf(TransportGroup);
    expect(testTracker.transport).toEqual({
      transportName: 'TransportGroup',
      usableTransports: [
        {
          transportName: 'QueuedTransport',
          queue: {
            queueName: 'TrackerQueue',
            batchDelayMs: 1000,
            batchSize: 10,
            concurrency: 4,
            processFunction: expect.any(Function),
            processingEventIds: [],
            store: {
              queueStoreName: 'TrackerQueueMemoryStore',
              length: 0,
              events: [],
            },
          },
          transport: {
            transportName: 'RetryTransport',
            maxAttempts: 10,
            maxRetryMs: Infinity,
            maxTimeoutMs: Infinity,
            minTimeoutMs: 1000,
            retryFactor: 2,
            attempts: [],
            transport: {
              transportName: 'TransportSwitch',
              firstUsableTransport: {
                transportName: 'FetchAPITransport',
                endpoint: 'localhost',
                fetchFunction: defaultFetchFunction,
              },
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
    const testTracker = new BrowserTracker({
      applicationId: 'app-id',
      transport: new FetchAPITransport({ endpoint: 'localhost' }),
    });
    expect(testTracker).toBeInstanceOf(BrowserTracker);
    expect(testTracker.transport).toBeInstanceOf(FetchAPITransport);
  });

  describe('Default Plugins', () => {
    it('should have some Web Plugins configured by default when no `plugins` have been specified', () => {
      const testTracker = new BrowserTracker({ applicationId: 'app-id', endpoint: 'localhost' });
      expect(testTracker).toBeInstanceOf(BrowserTracker);
      expect(testTracker.plugins?.list).toEqual(
        expect.arrayContaining([
          expect.objectContaining({ pluginName: 'WebDocumentContextPlugin' }),
          expect.objectContaining({ pluginName: 'WebDeviceContextPlugin' }),
        ])
      );
    });

    it('should not have any default Plugin configured when `plugins` have been overridden', () => {
      const testTracker = new BrowserTracker({
        applicationId: 'app-id',
        endpoint: 'localhost',
        plugins: new TrackerPlugins([]),
      });
      expect(testTracker).toBeInstanceOf(BrowserTracker);
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

    it('should auto-track Application, WebDocument and WebDevice Contexts as global_contexts by default', async () => {
      const testTracker = new BrowserTracker({ applicationId: 'app-id', endpoint: 'localhost' });
      const testEvent = new TrackerEvent({ _type: 'test-event' });
      expect(testTracker).toBeInstanceOf(BrowserTracker);
      expect(testEvent.global_contexts).toHaveLength(0);
      expect(testEvent.location_stack).toHaveLength(0);

      const trackedEvent = await testTracker.trackEvent(testEvent);

      expect(trackedEvent.location_stack).toHaveLength(1);
      expect(trackedEvent.location_stack).toEqual(
        expect.arrayContaining([
          expect.objectContaining({
            _type: 'WebDocumentContext',
            id: '#document',
            url: 'http://localhost/',
          }),
        ])
      );

      expect(trackedEvent.global_contexts).toHaveLength(2);
      expect(trackedEvent.global_contexts).toEqual(
        expect.arrayContaining([
          expect.objectContaining({
            _type: 'ApplicationContext',
            id: 'app-id',
          }),
          expect.objectContaining({
            _type: 'DeviceContext',
            id: 'device',
            user_agent: USER_AGENT_MOCK_VALUE,
          }),
        ])
      );
    });
  });
});
