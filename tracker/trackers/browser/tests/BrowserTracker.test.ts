/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { RootLocationContextFromURLPlugin } from '@objectiv/plugin-root-location-context-from-url';
import { expectToThrow, MockConsoleImplementation, LogTransport } from '@objectiv/testing-tools';
import {
  GlobalContextName,
  TrackerEvent,
  TrackerPlugins,
  TrackerQueue,
  TrackerQueueMemoryStore,
  TrackerTransportRetry,
} from '@objectiv/tracker-core';
import { defaultFetchFunction, FetchTransport } from '@objectiv/transport-fetch';
import fetchMock from 'jest-fetch-mock';
import { clear, mockUserAgent } from 'jest-useragent-mock';
import { BrowserTracker } from '../src/';

require('@objectiv/developer-tools');
globalThis.objectiv.devTools?.TrackerConsole.setImplementation(MockConsoleImplementation);
globalThis.objectiv.devTools?.EventRecorder.configure({ enabled: false });

describe('BrowserTracker', () => {
  beforeEach(() => {
    fetchMock.enableMocks();
  });

  afterEach(() => {
    fetchMock.resetMocks();
  });

  beforeEach(() => {
    jest.resetAllMocks();
  });

  it('should not instantiate without either `transport` or `endpoint`', () => {
    expectToThrow(
      () =>
        new BrowserTracker({
          applicationId: 'app-id',
        })
    );
  });

  it('should not instantiate with both `endpoint` and `transport`', () => {
    expectToThrow(
      () =>
        new BrowserTracker({
          applicationId: 'app-id',
          endpoint: 'localhost',
          transport: new FetchTransport({
            endpoint: 'localhost',
          }),
        })
    );
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
      lastRunTimestamp: 0,
      running: false,
      processFunction: expect.any(Function),
      processingEventIds: [],
      store: {
        queueStoreName: 'LocalStorageQueueStore',
        localStorageKey: 'objectiv-events-queue-app-id',
      },
    });
  });

  it('should instantiate with given `transport`', () => {
    const testTracker = new BrowserTracker({
      applicationId: 'app-id',
      transport: new LogTransport(),
    });
    expect(testTracker).toBeInstanceOf(BrowserTracker);
    expect(testTracker.transport).toBeInstanceOf(LogTransport);
  });

  it('should instantiate with given `queue`', () => {
    const testTracker = new BrowserTracker({
      applicationId: 'app-id',
      transport: new LogTransport(),
      queue: new TrackerQueue({ store: new TrackerQueueMemoryStore() }),
    });
    expect(testTracker).toBeInstanceOf(BrowserTracker);
    expect(testTracker.queue?.store).toBeInstanceOf(TrackerQueueMemoryStore);
  });

  describe('Default Plugins', () => {
    it('should have some Web Plugins configured by default when no `plugins` have been specified', () => {
      const testTracker = new BrowserTracker({ applicationId: 'app-id', transport: new LogTransport() });
      expect(testTracker).toBeInstanceOf(BrowserTracker);
      expect(testTracker.plugins?.plugins).toEqual(
        expect.arrayContaining([
          expect.objectContaining({ pluginName: 'ApplicationContextPlugin' }),
          expect.objectContaining({ pluginName: 'HttpContextPlugin' }),
          expect.objectContaining({ pluginName: 'PathContextFromURLPlugin' }),
          expect.objectContaining({ pluginName: 'RootLocationContextFromURLPlugin' }),
        ])
      );
    });

    it('should allow disabling all plugins, exception made for OpenTaxonomyValidationPlugin ', () => {
      const testTracker = new BrowserTracker({
        applicationId: 'app-id',
        transport: new LogTransport(),
        trackApplicationContext: false,
        trackHttpContext: false,
        trackPathContextFromURL: false,
        trackRootLocationContextFromURL: false,
      });
      expect(testTracker).toBeInstanceOf(BrowserTracker);
      expect(testTracker.plugins?.plugins).toEqual([
        expect.objectContaining({ pluginName: 'OpenTaxonomyValidationPlugin' }),
      ]);
    });

    it('should allow customizing a plugin, without affecting the existing ones', () => {
      const testTracker = new BrowserTracker({
        applicationId: 'app-id',
        transport: new LogTransport(),
        plugins: [
          new RootLocationContextFromURLPlugin({
            idFactoryFunction: () => 'test',
          }),
        ],
      });
      expect(testTracker).toBeInstanceOf(BrowserTracker);
      expect(testTracker.plugins?.plugins).toEqual([
        expect.objectContaining({ pluginName: 'OpenTaxonomyValidationPlugin' }),
        expect.objectContaining({ pluginName: 'ApplicationContextPlugin' }),
        expect.objectContaining({ pluginName: 'HttpContextPlugin' }),
        expect.objectContaining({ pluginName: 'PathContextFromURLPlugin' }),
        expect.objectContaining({ pluginName: 'RootLocationContextFromURLPlugin' }),
      ]);
    });

    it('should allow customizing the plugin set', () => {
      const testTracker = new BrowserTracker({
        applicationId: 'app-id',
        transport: new LogTransport(),
      });
      const trackerClone = new BrowserTracker({
        applicationId: 'app-id',
        transport: new LogTransport(),
        plugins: new TrackerPlugins({ tracker: testTracker, plugins: testTracker.plugins.plugins }),
      });

      expect(trackerClone).toBeInstanceOf(BrowserTracker);
      expect(trackerClone.plugins?.plugins).toEqual([
        expect.objectContaining({ pluginName: 'OpenTaxonomyValidationPlugin' }),
        expect.objectContaining({ pluginName: 'ApplicationContextPlugin' }),
        expect.objectContaining({ pluginName: 'HttpContextPlugin' }),
        expect.objectContaining({ pluginName: 'PathContextFromURLPlugin' }),
        expect.objectContaining({ pluginName: 'RootLocationContextFromURLPlugin' }),
      ]);
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

    it('should auto-track Application and Path Contexts by default', async () => {
      const testTracker = new BrowserTracker({ applicationId: 'app-id', transport: new LogTransport() });
      const testEvent = new TrackerEvent({ _type: 'test-event' });
      expect(testTracker).toBeInstanceOf(BrowserTracker);
      expect(testEvent.global_contexts).toHaveLength(0);
      expect(testEvent.location_stack).toHaveLength(0);

      const trackedEvent = await testTracker.trackEvent(testEvent);

      expect(trackedEvent.global_contexts).toHaveLength(3);
      expect(trackedEvent.global_contexts).toEqual(
        expect.arrayContaining([
          expect.objectContaining({
            _type: GlobalContextName.HttpContext,
            id: 'http_context',
          }),
          expect.objectContaining({
            _type: GlobalContextName.ApplicationContext,
            id: 'app-id',
          }),
          expect.objectContaining({
            _type: GlobalContextName.PathContext,
            id: 'http://localhost/',
          }),
        ])
      );
    });
  });
});
