import {
  ApplicationContextPlugin,
  ContextsConfig,
  Tracker,
  TrackerConfig,
  TrackerEvent,
  TrackerPluginInterface,
  TrackerPlugins,
  TrackerQueue,
  TrackerQueueMemoryStore,
} from '../src';
import { LogTransport } from './mocks/LogTransport';
import { mockConsole } from './mocks/MockConsole';
import { UnusableTransport } from './mocks/UnusableTransport';

describe('Tracker', () => {
  it('should instantiate with just applicationId', () => {
    jest.spyOn(console, 'log');
    expect(console.log).not.toHaveBeenCalled();
    const trackerConfig: TrackerConfig = { applicationId: 'app-id' };
    const testTracker = new Tracker(trackerConfig);
    expect(testTracker).toBeInstanceOf(Tracker);
    expect(testTracker.transport).toBe(undefined);
    expect(testTracker.plugins).toEqual({
      plugins: [
        {
          applicationContext: { __global_context: true, _type: 'ApplicationContext', id: 'app-id' },
          pluginName: 'ApplicationContextPlugin',
        },
      ],
    });
    expect(testTracker.applicationId).toBe('app-id');
    expect(testTracker.location_stack).toStrictEqual([]);
    expect(testTracker.global_contexts).toStrictEqual([]);
    expect(console.log).not.toHaveBeenCalled();
  });

  it('should instantiate with tracker config', async () => {
    expect(mockConsole.log).not.toHaveBeenCalled();
    const trackerConfig: TrackerConfig = { applicationId: 'app-id', console: mockConsole };
    const testTransport = new LogTransport();
    const testTracker = new Tracker({ ...trackerConfig, transport: testTransport });
    await expect(testTracker.waitForQueue()).resolves.toBe(true);
    expect(testTracker).toBeInstanceOf(Tracker);
    expect(testTracker.transport).toStrictEqual(testTransport);
    expect(testTracker.plugins).toEqual({
      plugins: [new ApplicationContextPlugin(trackerConfig)],
      console: mockConsole,
    });
    expect(testTracker.location_stack).toStrictEqual([]);
    expect(testTracker.global_contexts).toStrictEqual([]);
    expect(mockConsole.log).toHaveBeenNthCalledWith(1, 'Application ID: app-id');
  });

  it('should instantiate with another Tracker, inheriting its state, yet being independent instances', () => {
    const initialContextsState: TrackerConfig = {
      applicationId: 'app-id',
      location_stack: [
        { __location_context: true, _type: 'section', id: 'root' },
        { __location_context: true, _type: 'section', id: 'A' },
      ],
      global_contexts: [
        { __global_context: true, _type: 'global', id: 'A' },
        { __global_context: true, _type: 'global', id: 'B' },
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
    newTestTracker.location_stack.push({ __location_context: true, _type: 'section', id: 'X' });

    // The old tracker should be unaffected
    expect(testTracker.location_stack).toEqual(initialContextsState.location_stack);
    expect(testTracker.global_contexts).toEqual(initialContextsState.global_contexts);

    // While the new Tracker should now have a deeper Location Stack
    expect(newTestTracker.location_stack).toEqual([
      { __location_context: true, _type: 'section', id: 'root' },
      { __location_context: true, _type: 'section', id: 'A' },
      { __location_context: true, _type: 'section', id: 'X' },
    ]);
    expect(newTestTracker.global_contexts).toEqual([
      { __global_context: true, _type: 'global', id: 'A' },
      { __global_context: true, _type: 'global', id: 'B' },
    ]);
  });

  it('should allow complex compositions of multiple Tracker instances and Configs', () => {
    const mainTrackerContexts: TrackerConfig = {
      applicationId: 'app-id',
      location_stack: [
        { __location_context: true, _type: 'section', id: 'root' },
        { __location_context: true, _type: 'section', id: 'A' },
      ],
      global_contexts: [
        { __global_context: true, _type: 'global', id: 'X' },
        { __global_context: true, _type: 'global', id: 'Y' },
      ],
    };
    const mainTracker = new Tracker(mainTrackerContexts);

    // This new tracker is a clone of the mainTracker and extends it with two custom Contexts configuration
    const sectionTracker = new Tracker(
      mainTracker,
      {
        location_stack: [{ __location_context: true, _type: 'section', id: 'B' }],
        global_contexts: [{ __global_context: true, _type: 'global', id: 'Z' }],
      },
      {
        location_stack: [{ __location_context: true, _type: 'section', id: 'C' }],
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
      { __location_context: true, _type: 'section', id: 'root' },
      { __location_context: true, _type: 'section', id: 'A' },
      { __location_context: true, _type: 'section', id: 'B' },
      { __location_context: true, _type: 'section', id: 'C' },
    ]);
    expect(sectionTracker.global_contexts).toEqual([
      { __global_context: true, _type: 'global', id: 'X' },
      { __global_context: true, _type: 'global', id: 'Y' },
      { __global_context: true, _type: 'global', id: 'Z' },
    ]);
  });

  describe('trackEvent', () => {
    const eventContexts: ContextsConfig = {
      location_stack: [
        { __location_context: true, _type: 'section', id: 'B' },
        { __location_context: true, _type: 'item', id: 'C' },
      ],
      global_contexts: [
        { __global_context: true, _type: 'global', id: 'W' },
        { __global_context: true, _type: 'global', id: 'X' },
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
        console: mockConsole,
        transport: new LogTransport({ console: mockConsole }),
        applicationId: 'app-id',
        location_stack: [
          { __location_context: true, _type: 'section', id: 'root' },
          { __location_context: true, _type: 'section', id: 'A' },
        ],
        global_contexts: [
          { __global_context: true, _type: 'global', id: 'Y' },
          { __global_context: true, _type: 'global', id: 'Z' },
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
        { __location_context: true, _type: 'section', id: 'root' },
        { __location_context: true, _type: 'section', id: 'A' },
        { __location_context: true, _type: 'section', id: 'B' },
        { __location_context: true, _type: 'item', id: 'C' },
      ]);
      expect(trackedEvent.global_contexts).toStrictEqual([
        { __global_context: true, _type: 'global', id: 'W' },
        { __global_context: true, _type: 'global', id: 'X' },
        { __global_context: true, _type: 'global', id: 'Y' },
        { __global_context: true, _type: 'global', id: 'Z' },
        { __global_context: true, _type: 'ApplicationContext', id: 'app-id' },
      ]);
    });

    it('should execute all plugins implementing the initialize callback', () => {
      const pluginC: TrackerPluginInterface = { pluginName: 'pC', isUsable: () => true, initialize: jest.fn() };
      const pluginD: TrackerPluginInterface = { pluginName: 'pD', isUsable: () => true, initialize: jest.fn() };
      const trackerPlugins = new TrackerPlugins({ plugins: [pluginC, pluginD] });
      const testTracker = new Tracker({ ...trackerConfig, plugins: trackerPlugins, console: mockConsole });
      expect(pluginC.initialize).toHaveBeenCalledWith(testTracker);
      expect(pluginD.initialize).toHaveBeenCalledWith(testTracker);
    });

    it('should execute all plugins implementing the beforeTransport callback', () => {
      const pluginE: TrackerPluginInterface = {
        pluginName: 'pE',
        isUsable: () => true,
        beforeTransport: jest.fn(),
      };
      const pluginF: TrackerPluginInterface = {
        pluginName: 'pF',
        isUsable: () => true,
        beforeTransport: jest.fn(),
      };
      const trackerPlugins = new TrackerPlugins({ plugins: [pluginE, pluginF] });
      const testTracker = new Tracker({ applicationId: 'app-id', plugins: trackerPlugins });
      testTracker.trackEvent(testEvent);
      expect(pluginE.beforeTransport).toHaveBeenCalledWith(expect.objectContaining(testEvent));
      expect(pluginF.beforeTransport).toHaveBeenCalledWith(expect.objectContaining(testEvent));
    });

    it('should send the Event via the given TrackerTransport', () => {
      const testTransport = new LogTransport();
      jest.spyOn(testTransport, 'handle');
      const testTracker = new Tracker({ applicationId: 'app-id', transport: testTransport });
      testTracker.trackEvent(testEvent);
      expect(testTransport.handle).toHaveBeenCalledWith(expect.objectContaining({ _type: testEvent._type }));
    });

    it("should not send the Event via the given TrackerTransport if it's not usable", () => {
      const unusableTransport = new UnusableTransport();
      expect(unusableTransport.isUsable()).toEqual(false);
      jest.spyOn(unusableTransport, 'handle');
      const testTracker = new Tracker({ applicationId: 'app-id', transport: unusableTransport, console: mockConsole });
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
      const testTracker = new Tracker({ applicationId: 'app-id', transport: testTransport, console: mockConsole });
      jest.resetAllMocks();
      testTracker.setActive(false);
      testTracker.setActive(true);
      testTracker.setActive(false);
      testTracker.trackEvent(testEvent);
      expect(testTransport.handle).not.toHaveBeenCalled();
      expect(mockConsole.log).toHaveBeenCalledTimes(3);
      expect(mockConsole.log).toHaveBeenNthCalledWith(
        1,
        `%c｢objectiv:Tracker:app-id｣ New state: inactive`,
        'font-weight: bold'
      );
      expect(mockConsole.log).toHaveBeenNthCalledWith(
        2,
        `%c｢objectiv:Tracker:app-id｣ New state: active`,
        'font-weight: bold'
      );
      expect(mockConsole.log).toHaveBeenNthCalledWith(
        3,
        `%c｢objectiv:Tracker:app-id｣ New state: inactive`,
        'font-weight: bold'
      );
    });
  });

  describe('TrackerQueue', () => {
    const testEventName = 'test-event';
    const testContexts: ContextsConfig = {
      location_stack: [{ __location_context: true, _type: 'section', id: 'test' }],
      global_contexts: [{ __global_context: true, _type: 'global', id: 'test' }],
    };
    const testEvent = new TrackerEvent({ _type: testEventName, ...testContexts });

    beforeEach(() => {
      jest.useFakeTimers();
      jest.spyOn(global, 'setInterval');
    });

    afterEach(() => {
      jest.useRealTimers();
    });

    it('should not initialize the queue runner if the given transport is not usable', () => {
      const logTransport = new UnusableTransport();
      jest.spyOn(logTransport, 'handle');
      const trackerQueue = new TrackerQueue();

      const testTracker = new Tracker({
        applicationId: 'app-id',
        transport: logTransport,
        queue: trackerQueue,
      });
      jest.runAllTimers();

      expect(testTracker.transport?.isUsable()).toBe(false);
      expect(trackerQueue.store.length).toBe(0);
      expect(logTransport.handle).not.toHaveBeenCalled();
      expect(setInterval).not.toHaveBeenCalled();
    });

    it('should queue events in the TrackerQueue and send them in batches via the LogTransport', async () => {
      const logTransport = new LogTransport();
      const queueStore = new TrackerQueueMemoryStore();
      const trackerQueue = new TrackerQueue({ store: queueStore });

      const testTracker = new Tracker({
        applicationId: 'app-id',
        queue: trackerQueue,
        transport: logTransport,
      });
      await expect(testTracker.waitForQueue()).resolves.toBe(true);

      const testTrackerWithConsole = new Tracker({
        applicationId: 'app-id',
        queue: trackerQueue,
        transport: logTransport,
        console: mockConsole,
      });
      await expect(testTracker.waitForQueue({ timeoutMs: 1, intervalMs: 1 })).resolves.toBe(true);

      jest.spyOn(trackerQueue, 'processFunction');

      expect(testTracker.transport?.isUsable()).toBe(true);
      expect(testTrackerWithConsole.transport?.isUsable()).toBe(true);

      expect(trackerQueue.processFunction).not.toBeUndefined();
      expect(trackerQueue.processFunction).not.toHaveBeenCalled();
      expect(setInterval).toHaveBeenCalledTimes(2);

      await testTracker.trackEvent(testEvent);
      await testTrackerWithConsole.trackEvent(testEvent);

      expect(queueStore.length).toBe(2);
      expect(trackerQueue.processFunction).not.toHaveBeenCalled();

      await trackerQueue.run();

      expect(trackerQueue.processingEventIds).toHaveLength(0);
      expect(trackerQueue.processFunction).toHaveBeenCalledTimes(1);
      expect(trackerQueue.processFunction).toHaveBeenNthCalledWith(
        1,
        expect.objectContaining({
          id: testEvent.id,
        }),
        expect.objectContaining({
          id: testEvent.id,
        })
      );
    });

    it('should flush pending events', async () => {
      const logTransport = new LogTransport();
      const queueStore = new TrackerQueueMemoryStore();
      const trackerQueue = new TrackerQueue({ store: queueStore, concurrency: 1, batchSize: 1, batchDelayMs: 1 });

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
      expect(setInterval).toHaveBeenCalledTimes(1);

      await testTracker.trackEvent(testEvent);
      await testTracker.trackEvent(testEvent);
      await testTracker.trackEvent(testEvent);
      await testTracker.trackEvent(testEvent);

      testTracker.flushQueue();

      expect(queueStore.length).toBe(0);

      await trackerQueue.run();

      expect(trackerQueue.processingEventIds).toHaveLength(0);
      expect(trackerQueue.processFunction).not.toHaveBeenCalled();
    });
  });
});
