/*
 * Copyright 2021 Objectiv B.V.
 */

import { mockConsole } from '@objectiv/testing-tools';
import { TrackerEvent, TrackerPlugins, TrackerQueue, TrackerTransportRetry } from '@objectiv/tracker-core';
import { defaultFetchFunction, FetchTransport } from '@objectiv/transport-fetch';
import fetchMock from 'jest-fetch-mock';
import { clear, mockUserAgent } from 'jest-useragent-mock';
import { BrowserTracker } from '../src/';

describe('BrowserTracker', () => {
  beforeEach(() => {
    jest.spyOn(console, 'error').mockImplementation(() => {});
    jest.spyOn(console, 'group').mockImplementation(() => {});
    jest.spyOn(console, 'groupCollapsed').mockImplementation(() => {});
    jest.spyOn(console, 'log').mockImplementation(() => {});
  });
  afterEach(() => {
    jest.resetAllMocks();
  });

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
          transport: new FetchTransport({
            endpoint: 'localhost',
          }),
        })
    ).toThrow();
  });

  it('should instantiate with `applicationId` and `endpoint`', () => {
    const testTracker = new BrowserTracker({ applicationId: 'app-id', endpoint: 'localhost' });
    expect(testTracker).toBeInstanceOf(BrowserTracker);
    expect(testTracker.transport).toBeInstanceOf(TrackerTransportRetry);
    expect(testTracker.transport).toEqual({
      transportName: 'TrackerTransportRetry',
      maxAttempts: 10,
      maxRetryMs: Infinity,
      maxTimeoutMs: Infinity,
      minTimeoutMs: 1000,
      retryFactor: 2,
      attempts: [],
      transport: {
        transportName: 'TrackerTransportSwitch',
        firstUsableTransport: {
          transportName: 'FetchTransport',
          endpoint: 'localhost',
          fetchFunction: defaultFetchFunction,
        },
      },
    });
    expect(testTracker.queue).toBeInstanceOf(TrackerQueue);
    expect(testTracker.queue).toEqual({
      queueName: 'TrackerQueue',
      batchDelayMs: 1000,
      batchSize: 10,
      concurrency: 4,
      processFunction: expect.any(Function),
      processingEventIds: [],
      store: {
        queueStoreName: 'LocalStorageQueueStore',
        localStorageKey: 'objectiv-events-queue-app-id',
      },
    });
  });

  it('should instantiate with `transport`', () => {
    const testTracker = new BrowserTracker({
      applicationId: 'app-id',
      transport: new FetchTransport({ endpoint: 'localhost' }),
    });
    expect(testTracker).toBeInstanceOf(BrowserTracker);
    expect(testTracker.transport).toBeInstanceOf(FetchTransport);
  });

  describe('env sensitive logic', () => {
    const OLD_ENV = process.env;

    beforeEach(() => {
      process.env = { ...OLD_ENV };
    });

    afterAll(() => {
      process.env = OLD_ENV;
    });

    it('Tracker instance should automatically bind to global console', () => {
      process.env.NODE_ENV = 'dev';

      const testTracker = new BrowserTracker({
        applicationId: 'app-id',
        transport: new FetchTransport({ endpoint: 'localhost' }),
      });

      expect(testTracker.console).toEqual(console);
    });

    it('should not crash if NODE_ENV is undefined', () => {
      process.env.NODE_ENV = undefined;

      const testTracker = new BrowserTracker({
        applicationId: 'app-id',
        transport: new FetchTransport({ endpoint: 'localhost' }),
      });

      expect(testTracker.console).toEqual(undefined);
    });

    it('Should not automatically bind to global console if we are in dev mode and console has been specified', () => {
      process.env.NODE_ENV = 'dev';

      const testTracker = new BrowserTracker({
        applicationId: 'app-id',
        transport: new FetchTransport({ endpoint: 'localhost' }),
        console: mockConsole,
      });

      expect(testTracker.console).toEqual(mockConsole);
    });

    it('Should not automatically bind to global console if `null` has been specified ', () => {
      process.env.NODE_ENV = 'dev';

      const testTracker = new BrowserTracker({
        applicationId: 'app-id',
        transport: new FetchTransport({ endpoint: 'localhost' }),
        console: mockConsole,
      });

      expect(testTracker.console).toEqual(mockConsole);
    });
  });

  describe('Default Plugins', () => {
    it('should have some Web Plugins configured by default when no `plugins` have been specified', () => {
      const testTracker = new BrowserTracker({ applicationId: 'app-id', endpoint: 'localhost' });
      expect(testTracker).toBeInstanceOf(BrowserTracker);
      expect(testTracker.plugins?.plugins).toEqual(
        expect.arrayContaining([expect.objectContaining({ pluginName: 'WebDocumentContextPlugin' })])
      );
    });

    it('should not have any default Plugin configured when `plugins` have been overridden', () => {
      const testTracker = new BrowserTracker({
        applicationId: 'app-id',
        endpoint: 'localhost',
        plugins: new TrackerPlugins({ plugins: [] }),
      });
      expect(testTracker).toBeInstanceOf(BrowserTracker);
      expect(testTracker.plugins?.plugins).toStrictEqual([]);
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

    it('should auto-track Application and WebDocument Contexts by default', async () => {
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

      expect(trackedEvent.global_contexts).toHaveLength(1);
      expect(trackedEvent.global_contexts).toEqual(
        expect.arrayContaining([
          expect.objectContaining({
            _type: 'ApplicationContext',
            id: 'app-id',
          }),
        ])
      );
    });
  });
});
