/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { IdentityContextAttributes, IdentityContextPlugin } from '@objectiv/plugin-identity-context';
import { RootLocationContextFromURLPlugin } from '@objectiv/plugin-root-location-context-from-url';
import { AbstractGlobalContext } from '@objectiv/schema';
import { expectToThrow, MockConsoleImplementation } from '@objectiv/testing-tools';
import {
  GlobalContextName,
  makeIdentityContext,
  makeSuccessEvent,
  TrackerEvent,
  TrackerPlugins,
  TrackerQueue,
  TrackerQueueMemoryStore,
  TrackerTransportRetry,
} from '@objectiv/tracker-core';
import { DebugTransport } from '@objectiv/transport-debug';
import { defaultFetchFunction, FetchTransport } from '@objectiv/transport-fetch';
import fetchMock from 'jest-fetch-mock';
import { clear, mockUserAgent } from 'jest-useragent-mock';
import { ReactTracker, trackSuccessEvent } from '../src/';

require('@objectiv/developer-tools');
globalThis.objectiv.devTools?.TrackerConsole.setImplementation(MockConsoleImplementation);
globalThis.objectiv.devTools?.EventRecorder.configure({ enabled: false });

describe('ReactTracker', () => {
  beforeEach(() => {
    jest.resetAllMocks();
  });

  it('should not instantiate without either `transport` or `endpoint`', () => {
    expectToThrow(
      () =>
        new ReactTracker({
          applicationId: 'app-id',
        })
    );
  });

  it('should not instantiate with both `endpoint` and `transport`', () => {
    expectToThrow(
      () =>
        new ReactTracker({
          applicationId: 'app-id',
          endpoint: 'localhost',
          transport: new FetchTransport({
            endpoint: 'localhost',
          }),
        })
    );
  });

  it('should instantiate with `applicationId` and `endpoint`', () => {
    const testTracker = new ReactTracker({ applicationId: 'app-id', trackerId: 'app-id', endpoint: 'localhost' });
    expect(testTracker).toBeInstanceOf(ReactTracker);
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
    const testTracker = new ReactTracker({
      applicationId: 'app-id',
      transport: new FetchTransport({ endpoint: 'localhost' }),
    });
    expect(testTracker).toBeInstanceOf(ReactTracker);
    expect(testTracker.transport).toBeInstanceOf(FetchTransport);
  });

  it('should instantiate with given `queue`', () => {
    const testTracker = new ReactTracker({
      applicationId: 'app-id',
      endpoint: 'localhost',
      queue: new TrackerQueue({ store: new TrackerQueueMemoryStore() }),
    });
    expect(testTracker).toBeInstanceOf(ReactTracker);
    expect(testTracker.queue?.store).toBeInstanceOf(TrackerQueueMemoryStore);
  });

  describe('Default Plugins', () => {
    it('should have some Web Plugins configured by default when no `plugins` have been specified', () => {
      const testTracker = new ReactTracker({ applicationId: 'app-id', endpoint: 'localhost' });
      expect(testTracker).toBeInstanceOf(ReactTracker);
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
      const testTracker = new ReactTracker({
        applicationId: 'app-id',
        endpoint: 'localhost',
        trackApplicationContext: false,
        trackHttpContext: false,
        trackPathContextFromURL: false,
        trackRootLocationContextFromURL: false,
      });
      expect(testTracker).toBeInstanceOf(ReactTracker);
      expect(testTracker.plugins?.plugins).toEqual([
        expect.objectContaining({ pluginName: 'OpenTaxonomyValidationPlugin' }),
      ]);
    });

    it('should allow customizing a plugin, without affecting the existing ones', () => {
      const testTracker = new ReactTracker({
        applicationId: 'app-id',
        endpoint: 'localhost',
        plugins: [
          new RootLocationContextFromURLPlugin({
            idFactoryFunction: () => 'test',
          }),
        ],
      });
      expect(testTracker).toBeInstanceOf(ReactTracker);
      expect(testTracker.plugins?.plugins).toEqual([
        expect.objectContaining({ pluginName: 'OpenTaxonomyValidationPlugin' }),
        expect.objectContaining({ pluginName: 'ApplicationContextPlugin' }),
        expect.objectContaining({ pluginName: 'HttpContextPlugin' }),
        expect.objectContaining({ pluginName: 'PathContextFromURLPlugin' }),
        expect.objectContaining({ pluginName: 'RootLocationContextFromURLPlugin' }),
      ]);
    });

    it('should allow customizing the plugin set', () => {
      const testTracker = new ReactTracker({
        applicationId: 'app-id',
        endpoint: 'localhost',
      });
      const trackerClone = new ReactTracker({
        applicationId: 'app-id',
        endpoint: 'localhost',
        plugins: new TrackerPlugins({ tracker: testTracker, plugins: testTracker.plugins.plugins }),
      });

      expect(trackerClone).toBeInstanceOf(ReactTracker);
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

    it('should auto-track Application Context by default', async () => {
      const testTracker = new ReactTracker({ applicationId: 'app-id', transport: new DebugTransport() });
      const testEvent = new TrackerEvent({ _type: 'test-event' });
      expect(testTracker).toBeInstanceOf(ReactTracker);
      expect(testEvent.global_contexts).toHaveLength(0);

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

    it('should allow attaching arbitrary global contexts', async () => {
      /**
       * Mocked identity metadata we will use to enrich the event, via IdentityContext
       */
      const identityMetadata: IdentityContextAttributes = {
        id: 'authentication',
        value: '123abc',
      };

      /**
       * Our assertion helper function. The three tests below will expect the same result as verified here.
       */
      const expectGlobalContextsToContainIdentityContext = (globalContexts: AbstractGlobalContext[]) => {
        expect(globalContexts).toEqual(
          expect.arrayContaining([
            expect.objectContaining({ _type: GlobalContextName.HttpContext }),
            expect.objectContaining({ _type: GlobalContextName.ApplicationContext }),
            expect.objectContaining({ _type: GlobalContextName.PathContext }),
            expect.objectContaining({ _type: GlobalContextName.IdentityContext, ...identityMetadata }),
          ])
        );
      };

      /**
       * Test #1 - The IdentityContext is already part of the Tracker instance
       */
      const testTracker1 = new ReactTracker({ applicationId: 'app-id', transport: new DebugTransport() });
      testTracker1.global_contexts.push(makeIdentityContext(identityMetadata));
      expect(testTracker1.global_contexts).toHaveLength(2);
      expect(testTracker1.global_contexts).toEqual(
        expect.arrayContaining([
          expect.objectContaining({ _type: GlobalContextName.HttpContext }),
          expect.objectContaining({ _type: GlobalContextName.IdentityContext, ...identityMetadata }),
        ])
      );
      const successEvent1 = makeSuccessEvent({
        message: 'login successful',
      });
      const trackedEvent1 = await testTracker1.trackEvent(successEvent1);
      expectGlobalContextsToContainIdentityContext(trackedEvent1.global_contexts);

      /**
       * Test #2 - Add the IdentityContext to any Event Tracker method
       */
      const testTracker2 = new ReactTracker({ applicationId: 'app-id', transport: new DebugTransport() });
      expect(testTracker2.global_contexts).toHaveLength(1);
      expect(testTracker2.global_contexts).toEqual(
        expect.arrayContaining([expect.objectContaining({ _type: GlobalContextName.HttpContext })])
      );
      const trackedEvent2 = await trackSuccessEvent({
        tracker: testTracker2,
        message: 'Login successful',
        globalContexts: [makeIdentityContext(identityMetadata)],
      });
      expectGlobalContextsToContainIdentityContext(trackedEvent2.global_contexts);

      /**
       * Test #3 - Third method, add the IdentityContext to any Event Factory
       */
      const successEvent3 = makeSuccessEvent({
        message: 'login successful',
        global_contexts: [makeIdentityContext(identityMetadata)],
      });
      const trackedEvent3 = await testTracker1.trackEvent(successEvent3);
      expectGlobalContextsToContainIdentityContext(trackedEvent3.global_contexts);

      /**
       * Test #4 - Rely on IdentityContextPlugin to generate the IdentityContext when enriching before transport
       */
      const testTracker4 = new ReactTracker({
        applicationId: 'app-id',
        transport: new DebugTransport(),
        plugins: [new IdentityContextPlugin(identityMetadata)],
      });
      const successEvent4 = makeSuccessEvent({ message: 'login successful' });
      const trackedEvent4 = await testTracker4.trackEvent(successEvent4);
      expectGlobalContextsToContainIdentityContext(trackedEvent4.global_contexts);
    });
  });
});
