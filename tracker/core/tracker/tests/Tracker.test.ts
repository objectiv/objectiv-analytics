/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { ConfigurableMockTransport, LogTransport, matchUUID, MockConsoleImplementation } from '@objectiv/testing-tools';
import {
  ContextsConfig,
  generateUUID,
  GlobalContextName,
  LocationContextName,
  Tracker,
  TrackerConfig,
  TrackerEvent,
  TrackerPluginInterface,
  TrackerQueue,
  TrackerQueueMemoryStore,
} from '../src';

require('@objectiv/developer-tools');
globalThis.objectiv.devTools?.TrackerConsole.setImplementation(MockConsoleImplementation);
globalThis.objectiv.devTools?.EventRecorder.configure({ enabled: false });

describe('Tracker', () => {
  beforeEach(() => {
    jest.resetAllMocks();
  });

  it('should instantiate with just applicationId', () => {
    jest.spyOn(console, 'log');
    expect(console.log).not.toHaveBeenCalled();
    const trackerConfig: TrackerConfig = { applicationId: 'app-id' };
    const testTracker = new Tracker(trackerConfig);
    expect(testTracker).toBeInstanceOf(Tracker);
    expect(testTracker.transport).toBe(undefined);
    expect(testTracker.plugins.plugins).toEqual([
      {
        pluginName: 'OpenTaxonomyValidationPlugin',
        initialized: true,
        validationRules: [
          {
            validationRuleName: 'GlobalContextValidationRule',
            logPrefix: 'OpenTaxonomyValidationPlugin',
            contextName: GlobalContextName.ApplicationContext,
            platform: 'CORE',
            once: true,
            validate: expect.any(Function),
          },
          {
            validationRuleName: 'LocationContextValidationRule',
            logPrefix: 'OpenTaxonomyValidationPlugin',
            contextName: LocationContextName.RootLocationContext,
            platform: 'CORE',
            position: 0,
            once: true,
            validate: expect.any(Function),
            eventMatches: expect.any(Function),
          },
          {
            validationRuleName: 'GlobalContextValidationRule',
            logPrefix: 'OpenTaxonomyValidationPlugin',
            contextName: GlobalContextName.PathContext,
            platform: 'CORE',
            once: true,
            validate: expect.any(Function),
            eventMatches: expect.any(Function),
          },
        ],
      },
    ]);
    expect(testTracker.applicationId).toBe('app-id');
    expect(testTracker.location_stack).toStrictEqual([]);
    expect(testTracker.global_contexts).toStrictEqual([]);
    expect(console.log).not.toHaveBeenCalled();
  });

  it('should instantiate with tracker config', async () => {
    expect(MockConsoleImplementation.log).not.toHaveBeenCalled();
    const testTransport = new LogTransport();
    const testTracker = new Tracker({
      applicationId: 'app-id',
      transport: testTransport,
    });
    await expect(testTracker.waitForQueue()).resolves.toBe(true);
    expect(testTracker).toBeInstanceOf(Tracker);
    expect(testTracker.transport).toStrictEqual(testTransport);
    expect(testTracker.plugins.plugins).toEqual([
      {
        pluginName: 'OpenTaxonomyValidationPlugin',
        initialized: true,
        validationRules: [
          {
            validationRuleName: 'GlobalContextValidationRule',
            logPrefix: 'OpenTaxonomyValidationPlugin',
            contextName: GlobalContextName.ApplicationContext,
            platform: 'CORE',
            once: true,
            validate: expect.any(Function),
          },
          {
            validationRuleName: 'LocationContextValidationRule',
            logPrefix: 'OpenTaxonomyValidationPlugin',
            contextName: LocationContextName.RootLocationContext,
            platform: 'CORE',
            position: 0,
            once: true,
            validate: expect.any(Function),
            eventMatches: expect.any(Function),
          },
          {
            validationRuleName: 'GlobalContextValidationRule',
            logPrefix: 'OpenTaxonomyValidationPlugin',
            contextName: GlobalContextName.PathContext,
            platform: 'CORE',
            once: true,
            validate: expect.any(Function),
            eventMatches: expect.any(Function),
          },
        ],
      },
    ]);
    expect(testTracker.location_stack).toStrictEqual([]);
    expect(testTracker.global_contexts).toStrictEqual([]);
    expect(MockConsoleImplementation.log).toHaveBeenCalledWith('Application ID: app-id');
  });

  it('should instantiate with another Tracker, inheriting its state, yet being independent instances', () => {
    const initialContextsState: TrackerConfig = {
      applicationId: 'app-id',
      location_stack: [
        { __instance_id: generateUUID(), __location_context: true, _type: 'section', id: 'root' },
        { __instance_id: generateUUID(), __location_context: true, _type: 'section', id: 'A' },
      ],
      global_contexts: [
        { __instance_id: generateUUID(), __global_context: true, _type: 'global', id: 'A' },
        { __instance_id: generateUUID(), __global_context: true, _type: 'global', id: 'B' },
      ],
    };

    const testTracker = new Tracker(initialContextsState);
    expect(testTracker.location_stack).toEqual(initialContextsState.location_stack);
    expect(testTracker.global_contexts).toEqual(initialContextsState.global_contexts);

    // Create a clone of the existing tracker
    const newTestTracker = new Tracker(testTracker);
    expect(newTestTracker).toBeInstanceOf(Tracker);
    // They should be identical (yet separate instances)
    expect(newTestTracker).toEqual(testTracker);

    // Refine Location Stack of the new Tracker with an extra Section
    newTestTracker.location_stack.push({
      __instance_id: generateUUID(),
      __location_context: true,
      _type: 'section',
      id: 'X',
    });

    // The old tracker should be unaffected
    expect(testTracker.location_stack).toEqual(initialContextsState.location_stack);
    expect(testTracker.global_contexts).toEqual(initialContextsState.global_contexts);

    // While the new Tracker should now have a deeper Location Stack
    expect(newTestTracker.location_stack).toEqual([
      { __instance_id: matchUUID, __location_context: true, _type: 'section', id: 'root' },
      { __instance_id: matchUUID, __location_context: true, _type: 'section', id: 'A' },
      { __instance_id: matchUUID, __location_context: true, _type: 'section', id: 'X' },
    ]);
    expect(newTestTracker.global_contexts).toEqual([
      { __instance_id: matchUUID, __global_context: true, _type: 'global', id: 'A' },
      { __instance_id: matchUUID, __global_context: true, _type: 'global', id: 'B' },
    ]);
  });

  it('should allow complex compositions of multiple Tracker instances and Configs', () => {
    const mainTrackerContexts: TrackerConfig = {
      applicationId: 'app-id',
      location_stack: [
        { __instance_id: generateUUID(), __location_context: true, _type: 'section', id: 'root' },
        { __instance_id: generateUUID(), __location_context: true, _type: 'section', id: 'A' },
      ],
      global_contexts: [
        { __instance_id: generateUUID(), __global_context: true, _type: 'global', id: 'X' },
        { __instance_id: generateUUID(), __global_context: true, _type: 'global', id: 'Y' },
      ],
    };
    const mainTracker = new Tracker(mainTrackerContexts);

    // This new tracker is a clone of the mainTracker and extends it with two custom Contexts configuration
    const sectionTracker = new Tracker(
      mainTracker,
      {
        location_stack: [{ __instance_id: generateUUID(), __location_context: true, _type: 'section', id: 'B' }],
        global_contexts: [{ __instance_id: generateUUID(), __global_context: true, _type: 'global', id: 'Z' }],
      },
      {
        location_stack: [{ __instance_id: generateUUID(), __location_context: true, _type: 'section', id: 'C' }],
      },
      // These last two configurations are useless, but we want to make sure nothing breaks with them
      {
        global_contexts: [],
      },
      {}
    );

    // The old tracker should be unaffected
    expect(mainTracker.location_stack).toEqual(mainTrackerContexts.location_stack);
    expect(mainTracker.global_contexts).toEqual(mainTrackerContexts.global_contexts);

    // The new Tracker, instead, should have all of the Contexts of the mainTracker + the extra Config provided
    expect(sectionTracker.location_stack).toEqual([
      { __instance_id: matchUUID, __location_context: true, _type: 'section', id: 'root' },
      { __instance_id: matchUUID, __location_context: true, _type: 'section', id: 'A' },
      { __instance_id: matchUUID, __location_context: true, _type: 'section', id: 'B' },
      { __instance_id: matchUUID, __location_context: true, _type: 'section', id: 'C' },
    ]);
    expect(sectionTracker.global_contexts).toEqual([
      { __instance_id: matchUUID, __global_context: true, _type: 'global', id: 'X' },
      { __instance_id: matchUUID, __global_context: true, _type: 'global', id: 'Y' },
      { __instance_id: matchUUID, __global_context: true, _type: 'global', id: 'Z' },
    ]);
  });

  describe('trackEvent', () => {
    const eventContexts: ContextsConfig = {
      location_stack: [
        { __instance_id: generateUUID(), __location_context: true, _type: 'section', id: 'B' },
        { __instance_id: generateUUID(), __location_context: true, _type: 'item', id: 'C' },
      ],
      global_contexts: [
        { __instance_id: generateUUID(), __global_context: true, _type: 'global', id: 'W' },
        { __instance_id: generateUUID(), __global_context: true, _type: 'global', id: 'X' },
      ],
    };
    const testEvent = new TrackerEvent(
      {
        _type: 'test-event',
      },
      eventContexts
    );
    const trackerConfig: TrackerConfig = { applicationId: 'app-id' };

    it('should merge Tracker Location Stack and Global Contexts with the Event ones', async () => {
      const trackerContexts: TrackerConfig = {
        transport: new LogTransport(),
        applicationId: 'app-id',
        location_stack: [
          { __instance_id: generateUUID(), __location_context: true, _type: 'section', id: 'root' },
          { __instance_id: generateUUID(), __location_context: true, _type: 'section', id: 'A' },
        ],
        global_contexts: [
          { __instance_id: generateUUID(), __global_context: true, _type: 'global', id: 'Y' },
          { __instance_id: generateUUID(), __global_context: true, _type: 'global', id: 'Z' },
        ],
      };
      const testTracker = new Tracker(trackerContexts);
      expect(testEvent.location_stack).toStrictEqual(eventContexts.location_stack);
      expect(testEvent.global_contexts).toStrictEqual(eventContexts.global_contexts);
      const trackedEvent = await testTracker.trackEvent(testEvent);
      expect(testEvent.location_stack).toStrictEqual(eventContexts.location_stack);
      expect(testEvent.global_contexts).toStrictEqual(eventContexts.global_contexts);
      expect(testTracker.location_stack).toStrictEqual(trackerContexts.location_stack);
      expect(testTracker.global_contexts).toStrictEqual(trackerContexts.global_contexts);
      expect(trackedEvent.location_stack).toStrictEqual([
        { __instance_id: matchUUID, __location_context: true, _type: 'section', id: 'root' },
        { __instance_id: matchUUID, __location_context: true, _type: 'section', id: 'A' },
        { __instance_id: matchUUID, __location_context: true, _type: 'section', id: 'B' },
        { __instance_id: matchUUID, __location_context: true, _type: 'item', id: 'C' },
      ]);
      expect(trackedEvent.global_contexts).toStrictEqual([
        { __instance_id: matchUUID, __global_context: true, _type: 'global', id: 'W' },
        { __instance_id: matchUUID, __global_context: true, _type: 'global', id: 'X' },
        { __instance_id: matchUUID, __global_context: true, _type: 'global', id: 'Y' },
        { __instance_id: matchUUID, __global_context: true, _type: 'global', id: 'Z' },
      ]);
    });

    it('should execute all plugins implementing the initialize callback', () => {
      const pluginC: TrackerPluginInterface = { pluginName: 'pC', isUsable: () => true, initialize: jest.fn() };
      const pluginD: TrackerPluginInterface = { pluginName: 'pD', isUsable: () => true, initialize: jest.fn() };
      const testTracker = new Tracker({ ...trackerConfig, plugins: [pluginC, pluginD] });
      expect(pluginC.initialize).toHaveBeenCalledWith(testTracker);
      expect(pluginD.initialize).toHaveBeenCalledWith(testTracker);
    });

    it('should execute all plugins implementing the enrich callback', () => {
      const pluginE: TrackerPluginInterface = {
        pluginName: 'pE',
        isUsable: () => true,
        enrich: jest.fn(),
      };
      const pluginF: TrackerPluginInterface = {
        pluginName: 'pF',
        isUsable: () => true,
        enrich: jest.fn(),
      };
      const testTracker = new Tracker({
        applicationId: 'app-id',
        plugins: [pluginE, pluginF],
      });
      testTracker.trackEvent(testEvent);
      expect(pluginE.enrich).toHaveBeenCalledWith(expect.objectContaining({ _type: 'test-event' }));
      expect(pluginF.enrich).toHaveBeenCalledWith(expect.objectContaining({ _type: 'test-event' }));
    });

    it('should execute all plugins implementing the validate callback', () => {
      const pluginE: TrackerPluginInterface = {
        pluginName: 'pE',
        isUsable: () => true,
        validate: jest.fn(),
      };
      const pluginF: TrackerPluginInterface = {
        pluginName: 'pF',
        isUsable: () => true,
        validate: jest.fn(),
      };
      const testTracker = new Tracker({ applicationId: 'app-id', plugins: [pluginE, pluginF] });
      testTracker.trackEvent(testEvent);
      expect(pluginE.validate).toHaveBeenCalledWith(expect.objectContaining({ _type: 'test-event' }));
      expect(pluginF.validate).toHaveBeenCalledWith(expect.objectContaining({ _type: 'test-event' }));
    });

    it('should send the Event via the given TrackerTransport', () => {
      const testTransport = new LogTransport();
      jest.spyOn(testTransport, 'handle');
      const testTracker = new Tracker({ applicationId: 'app-id', transport: testTransport });
      testTracker.trackEvent(testEvent);
      expect(testTransport.handle).toHaveBeenCalledWith(expect.objectContaining({ _type: testEvent._type }));
    });

    it("should not send the Event via the given TrackerTransport if it's not usable", () => {
      const unusableTransport = new ConfigurableMockTransport({ isUsable: false });
      expect(unusableTransport.isUsable()).toEqual(false);
      jest.spyOn(unusableTransport, 'handle');
      const testTracker = new Tracker({ applicationId: 'app-id', transport: unusableTransport });
      testTracker.trackEvent(testEvent);
      expect(unusableTransport.handle).not.toHaveBeenCalled();
    });

    it('should not send the Event when tracker has been deactivated', () => {
      const testTransport = new LogTransport();
      jest.spyOn(testTransport, 'handle');
      const testTracker = new Tracker({ applicationId: 'app-id', transport: testTransport, active: false });
      testTracker.trackEvent(testEvent);
      expect(testTransport.handle).not.toHaveBeenCalled();
      testTracker.setActive(false);
      testTracker.trackEvent(testEvent);
      expect(testTransport.handle).not.toHaveBeenCalled();
      testTracker.setActive(true);
      testTracker.trackEvent(testEvent);
      expect(testTransport.handle).toHaveBeenCalledWith(expect.objectContaining({ _type: testEvent._type }));
    });

    it('should console.log when Tracker changes active state', () => {
      const testTransport = new LogTransport();
      jest.spyOn(testTransport, 'handle');
      const testTracker = new Tracker({
        applicationId: 'app-id',
        transport: testTransport,
      });
      testTracker.plugins.plugins = [];
      jest.resetAllMocks();
      testTracker.setActive(false);
      testTracker.setActive(true);
      testTracker.setActive(false);
      testTracker.trackEvent(testEvent);
      expect(testTransport.handle).not.toHaveBeenCalled();
      expect(MockConsoleImplementation.log).toHaveBeenCalledTimes(3);
      expect(MockConsoleImplementation.log).toHaveBeenNthCalledWith(
        1,
        `%c｢objectiv:Tracker:app-id｣ New state: inactive`,
        'font-weight: bold'
      );
      expect(MockConsoleImplementation.log).toHaveBeenNthCalledWith(
        2,
        `%c｢objectiv:Tracker:app-id｣ New state: active`,
        'font-weight: bold'
      );
      expect(MockConsoleImplementation.log).toHaveBeenNthCalledWith(
        3,
        `%c｢objectiv:Tracker:app-id｣ New state: inactive`,
        'font-weight: bold'
      );
    });

    it('should wait and/or flush the queue according to the given options', async () => {
      const testTracker = new Tracker({ applicationId: 'app-id' });

      // Default > no waiting and no flush
      jest.spyOn(testTracker, 'flushQueue');
      jest.spyOn(testTracker, 'waitForQueue').mockResolvedValue(true);
      expect(testTracker.flushQueue).not.toHaveBeenCalled();
      expect(testTracker.waitForQueue).not.toHaveBeenCalled();
      await testTracker.trackEvent(testEvent);
      expect(testTracker.waitForQueue).not.toHaveBeenCalled();
      expect(testTracker.flushQueue).not.toHaveBeenCalled();

      jest.resetAllMocks();

      // FlushQueue `true` > no waiting and flush
      jest.spyOn(testTracker, 'flushQueue');
      jest.spyOn(testTracker, 'waitForQueue').mockResolvedValue(true);
      expect(testTracker.flushQueue).not.toHaveBeenCalled();
      expect(testTracker.waitForQueue).not.toHaveBeenCalled();
      await testTracker.trackEvent(testEvent, { flushQueue: true });
      expect(testTracker.waitForQueue).not.toHaveBeenCalled();
      expect(testTracker.flushQueue).toHaveBeenCalledTimes(1);

      jest.resetAllMocks();

      // FlushQueue `onTimeout` and waitForQueue not configured > no waiting and no flush
      jest.spyOn(testTracker, 'flushQueue');
      jest.spyOn(testTracker, 'waitForQueue').mockResolvedValue(true);
      expect(testTracker.flushQueue).not.toHaveBeenCalled();
      expect(testTracker.waitForQueue).not.toHaveBeenCalled();
      await testTracker.trackEvent(testEvent, { flushQueue: 'onTimeout' });
      expect(testTracker.waitForQueue).not.toHaveBeenCalled();
      expect(testTracker.flushQueue).not.toHaveBeenCalled();

      jest.resetAllMocks();

      // FlushQueue: `onTimeout` and waitForQueue `true` and not timed out > waiting and no flush
      jest.spyOn(testTracker, 'flushQueue');
      jest.spyOn(testTracker, 'waitForQueue').mockResolvedValue(true);
      expect(testTracker.flushQueue).not.toHaveBeenCalled();
      expect(testTracker.waitForQueue).not.toHaveBeenCalled();
      await testTracker.trackEvent(testEvent, { waitForQueue: true, flushQueue: 'onTimeout' });
      expect(testTracker.waitForQueue).toHaveBeenCalledTimes(1);
      expect(testTracker.flushQueue).not.toHaveBeenCalled();

      jest.resetAllMocks();

      // FlushQueue: `onTimeout` and waitForQueue `true` and timed out > waiting and flush
      jest.spyOn(testTracker, 'flushQueue');
      jest.spyOn(testTracker, 'waitForQueue').mockResolvedValue(true);
      expect(testTracker.flushQueue).not.toHaveBeenCalled();
      expect(testTracker.waitForQueue).not.toHaveBeenCalled();
      await testTracker.trackEvent(testEvent, { waitForQueue: true, flushQueue: true });
      expect(testTracker.waitForQueue).toHaveBeenCalledTimes(1);
      expect(testTracker.flushQueue).toHaveBeenCalledTimes(1);

      jest.resetAllMocks();

      // FlushQueue: `onTimeout` and waitForQueue `{ intervalMs: 100 }` and timed out > waiting and flush
      jest.spyOn(testTracker, 'flushQueue');
      jest.spyOn(testTracker, 'waitForQueue').mockResolvedValue(true);
      expect(testTracker.flushQueue).not.toHaveBeenCalled();
      expect(testTracker.waitForQueue).not.toHaveBeenCalled();
      await testTracker.trackEvent(testEvent, { waitForQueue: { intervalMs: 100 }, flushQueue: true });
      expect(testTracker.waitForQueue).toHaveBeenCalledTimes(1);
      expect(testTracker.flushQueue).toHaveBeenCalledTimes(1);
    });
  });

  describe('TrackerQueue', () => {
    const testEventName = 'test-event';
    const testContexts: ContextsConfig = {
      location_stack: [{ __instance_id: generateUUID(), __location_context: true, _type: 'section', id: 'test' }],
      global_contexts: [{ __instance_id: generateUUID(), __global_context: true, _type: 'global', id: 'test' }],
    };
    const testEvent1 = new TrackerEvent({ _type: testEventName, ...testContexts });
    const testEvent2 = new TrackerEvent({ _type: testEventName, ...testContexts });
    const processFunctionSpy = jest.fn(() => Promise.resolve());

    beforeEach(() => {
      jest.useFakeTimers();
      jest.spyOn(global, 'setInterval');
    });

    afterEach(() => {
      jest.useRealTimers();
    });

    it('should not initialize the queue runner if the given transport is not usable', () => {
      const logTransport = new ConfigurableMockTransport({ isUsable: false });
      jest.spyOn(logTransport, 'handle');
      const trackerQueue = new TrackerQueue();
      trackerQueue.setProcessFunction(processFunctionSpy);

      const testTracker = new Tracker({
        applicationId: 'app-id',
        transport: logTransport,
        queue: trackerQueue,
      });

      expect(testTracker.transport?.isUsable()).toBe(false);
      expect(trackerQueue.store.length).toBe(0);
      expect(logTransport.handle).not.toHaveBeenCalled();
      expect(setInterval).not.toHaveBeenCalled();
    });

    it('should queue events in the TrackerQueue and send them in batches via the LogTransport', async () => {
      const logTransport = new LogTransport();
      const queueStore1 = new TrackerQueueMemoryStore();
      const queueStore2 = new TrackerQueueMemoryStore();
      const trackerQueue1 = new TrackerQueue({ store: queueStore1, batchDelayMs: 1 });
      const trackerQueue2 = new TrackerQueue({ store: queueStore2, batchDelayMs: 1 });
      trackerQueue1.setProcessFunction(processFunctionSpy);
      trackerQueue2.setProcessFunction(processFunctionSpy);

      const testTracker = new Tracker({
        applicationId: 'app-id',
        queue: trackerQueue1,
        transport: logTransport,
      });
      await expect(testTracker.waitForQueue()).resolves.toBe(true);

      const testTrackerWithConsole = new Tracker({
        applicationId: 'app-id',
        queue: trackerQueue2,
        transport: logTransport,
      });
      await expect(testTracker.waitForQueue({ timeoutMs: 1, intervalMs: 1 })).resolves.toBe(true);

      jest.spyOn(trackerQueue1, 'processFunction');
      jest.spyOn(trackerQueue2, 'processFunction');

      expect(testTracker.transport?.isUsable()).toBe(true);
      expect(testTrackerWithConsole.transport?.isUsable()).toBe(true);

      expect(trackerQueue1.processFunction).not.toBeUndefined();
      expect(trackerQueue1.processFunction).not.toHaveBeenCalled();
      expect(trackerQueue2.processFunction).not.toBeUndefined();
      expect(trackerQueue2.processFunction).not.toHaveBeenCalled();

      await testTracker.trackEvent(testEvent1);
      expect(trackerQueue1.processingEventIds).toHaveLength(0);
      expect(trackerQueue1.processFunction).toHaveBeenCalledTimes(1);
      expect(trackerQueue1.processFunction).toHaveBeenNthCalledWith(
        1,
        expect.objectContaining({
          id: testEvent1.id,
        })
      );

      await testTrackerWithConsole.trackEvent(testEvent2);
      expect(trackerQueue2.processingEventIds).toHaveLength(0);
      expect(trackerQueue2.processFunction).toHaveBeenCalledTimes(1);
      expect(trackerQueue2.processFunction).toHaveBeenNthCalledWith(
        1,
        expect.objectContaining({
          id: testEvent2.id,
        })
      );
    });

    it('should flush pending events', async () => {
      const logTransport = new LogTransport();
      const queueStore = new TrackerQueueMemoryStore();
      const trackerQueue = new TrackerQueue({ store: queueStore, concurrency: 1, batchSize: 1, batchDelayMs: 1 });
      trackerQueue.setProcessFunction(processFunctionSpy);

      const trackerWithoutQueue = new Tracker({
        applicationId: 'app-id',
        transport: logTransport,
      });
      // Should be safe to call when no queue has been specified
      trackerWithoutQueue.flushQueue();

      const testTracker = new Tracker({
        applicationId: 'app-id',
        queue: trackerQueue,
        transport: logTransport,
      });

      jest.spyOn(trackerQueue, 'processFunction');

      expect(testTracker.transport?.isUsable()).toBe(true);

      expect(trackerQueue.processFunction).not.toBeUndefined();
      expect(trackerQueue.processFunction).not.toHaveBeenCalled();

      await testTracker.queue?.store.write(testEvent1, testEvent2);

      expect(queueStore.length).toBe(2);

      testTracker.flushQueue();

      expect(queueStore.length).toBe(0);

      await trackerQueue.run();

      expect(trackerQueue.processingEventIds).toHaveLength(0);
      expect(trackerQueue.processFunction).not.toHaveBeenCalled();
    });
  });
});

describe('Without developer tools', () => {
  let objectivGlobal = globalThis.objectiv;

  beforeEach(() => {
    jest.clearAllMocks();
    globalThis.objectiv.devTools = undefined;
  });

  afterEach(() => {
    globalThis.objectiv = objectivGlobal;
  });

  it('Tracker should instantiate without validation rules and not log to TrackerConsole', async () => {
    expect(MockConsoleImplementation.log).not.toHaveBeenCalled();
    const testTransport = new LogTransport();
    const testQueue = new TrackerQueue();
    const testTracker = new Tracker({
      applicationId: 'app-id',
      transport: testTransport,
      queue: testQueue,
    });
    await expect(testTracker.waitForQueue()).resolves.toBe(true);
    expect(testTracker).toBeInstanceOf(Tracker);
    expect(testTracker.transport).toStrictEqual(testTransport);
    expect(testTracker.location_stack).toStrictEqual([]);
    expect(testTracker.global_contexts).toStrictEqual([]);
    expect(MockConsoleImplementation.log).not.toHaveBeenCalled();
  });
});
