/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { MockConsoleImplementation } from '@objectiv/testing-tools';
import { GlobalContextName, TrackerEvent, TrackerQueue, TrackerTransportRetry } from '@objectiv/tracker-core';
import { DebugTransport } from '@objectiv/transport-debug';
import { defaultFetchFunction, FetchTransport } from '@objectiv/transport-fetch';
import fetchMock from 'jest-fetch-mock';
import { ReactNativeTracker } from '../src/';

require('@objectiv/developer-tools');
globalThis.objectiv?.TrackerConsole.setImplementation(MockConsoleImplementation);

describe('ReactNativeTracker', () => {
  beforeEach(() => {
    jest.resetAllMocks();
  });

  it('should not instantiate without either `transport` or `endpoint`', () => {
    expect(
      () =>
        new ReactNativeTracker({
          applicationId: 'app-id',
        })
    ).toThrow();
  });

  it('should not instantiate with both `endpoint` and `transport`', () => {
    expect(
      () =>
        new ReactNativeTracker({
          applicationId: 'app-id',
          endpoint: 'localhost',
          transport: new FetchTransport({
            endpoint: 'localhost',
          }),
        })
    ).toThrow();
  });

  it('should instantiate with `applicationId` and `endpoint`', () => {
    const testTracker = new ReactNativeTracker({ applicationId: 'app-id', trackerId: 'app-id', endpoint: 'localhost' });
    expect(testTracker).toBeInstanceOf(ReactNativeTracker);
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
        transportName: 'FetchTransport',
        endpoint: 'localhost',
        fetchFunction: defaultFetchFunction,
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
        queueStoreName: 'TrackerQueueMemoryStore',
        events: [],
      },
    });
  });

  it('should instantiate with given `transport`', () => {
    const testTracker = new ReactNativeTracker({
      applicationId: 'app-id',
      transport: new FetchTransport({ endpoint: 'localhost' }),
    });
    expect(testTracker).toBeInstanceOf(ReactNativeTracker);
    expect(testTracker.transport).toBeInstanceOf(FetchTransport);
  });

  describe('Default Plugins', () => {
    it('should have some Web Plugins configured by default when no `plugins` have been specified', () => {
      const testTracker = new ReactNativeTracker({ applicationId: 'app-id', endpoint: 'localhost' });
      expect(testTracker).toBeInstanceOf(ReactNativeTracker);
      expect(testTracker.plugins?.plugins).toEqual(
        expect.arrayContaining([expect.objectContaining({ pluginName: 'ApplicationContextPlugin' })])
      );
    });

    it('should add Plugins `plugins` has been specified', () => {
      const testTracker = new ReactNativeTracker({
        applicationId: 'app-id',
        endpoint: 'localhost',
        plugins: [
          {
            pluginName: 'TestPlugin',
            isUsable() {
              return true;
            },
          },
        ],
      });
      expect(testTracker).toBeInstanceOf(ReactNativeTracker);
      expect(testTracker.plugins?.plugins).toEqual(
        expect.arrayContaining([
          expect.objectContaining({ pluginName: 'ApplicationContextPlugin' }),
          expect.objectContaining({ pluginName: 'TestPlugin' }),
        ])
      );
    });
  });

  describe('trackEvent', () => {
    beforeEach(() => {
      fetchMock.enableMocks();
    });

    afterEach(() => {
      fetchMock.resetMocks();
    });

    it('should auto-track Application Context by default', async () => {
      const testTracker = new ReactNativeTracker({ applicationId: 'app-id', transport: new DebugTransport() });
      const testEvent = new TrackerEvent({ _type: 'test-event' });
      expect(testTracker).toBeInstanceOf(ReactNativeTracker);
      expect(testEvent.global_contexts).toHaveLength(0);

      const trackedEvent = await testTracker.trackEvent(testEvent);

      expect(trackedEvent.global_contexts).toHaveLength(1);
      expect(trackedEvent.global_contexts).toEqual(
        expect.arrayContaining([
          expect.objectContaining({
            _type: GlobalContextName.ApplicationContext,
            id: 'app-id',
          }),
        ])
      );
    });
  });
});
