import { ContextsConfig, Tracker, TrackerEvent, TrackerPlugin, TrackerPlugins } from '../src';
import { LogTransport, noop, UnusableTransport } from './mocks';

describe('Tracker', () => {
  it('should instantiate without any config', () => {
    const testTracker = new Tracker();
    expect(testTracker).toBeInstanceOf(Tracker);
    expect(testTracker.transport).toBe(undefined);
    expect(testTracker.plugins).toBe(undefined);
    expect(testTracker.locationStack).toStrictEqual([]);
    expect(testTracker.globalContexts).toStrictEqual([]);
  });

  it('should instantiate with tracker config', () => {
    const testTransport = new LogTransport();
    const testTracker = new Tracker({ transport: testTransport });
    expect(testTracker).toBeInstanceOf(Tracker);
    expect(testTracker.transport).toStrictEqual(testTransport);
    expect(testTracker.plugins).toBe(undefined);
    expect(testTracker.locationStack).toStrictEqual([]);
    expect(testTracker.globalContexts).toStrictEqual([]);
  });

  it('should instantiate with another Tracker, inheriting its state, yet being independent instances', () => {
    const initialContextsState: ContextsConfig = {
      locationStack: [
        { _location_context: true, _context_type: 'section', id: 'root' },
        { _location_context: true, _context_type: 'section', id: 'A' },
      ],
      globalContexts: [
        { _global_context: true, _context_type: 'global', id: 'A' },
        { _global_context: true, _context_type: 'global', id: 'B' },
      ],
    };

    const testTracker = new Tracker(initialContextsState);
    expect(testTracker.locationStack).toEqual(initialContextsState.locationStack);
    expect(testTracker.globalContexts).toEqual(initialContextsState.globalContexts);

    // Create a clone of the existing tracker
    const newTestTracker = new Tracker(testTracker);
    expect(newTestTracker).toBeInstanceOf(Tracker);
    // They should be identical (yet separate instances)
    expect(newTestTracker).toEqual(testTracker);

    // Refine Location Stack of the new Tracker with an extra Section
    newTestTracker.locationStack.push({ _location_context: true, _context_type: 'section', id: 'X' });

    // The old tracker should be unaffected
    expect(testTracker.locationStack).toEqual(initialContextsState.locationStack);
    expect(testTracker.globalContexts).toEqual(initialContextsState.globalContexts);

    // While the new Tracker should now have a deeper Location Stack
    expect(newTestTracker.locationStack).toEqual([
      { _location_context: true, _context_type: 'section', id: 'root' },
      { _location_context: true, _context_type: 'section', id: 'A' },
      { _location_context: true, _context_type: 'section', id: 'X' },
    ]);
    expect(newTestTracker.globalContexts).toEqual([
      { _global_context: true, _context_type: 'global', id: 'A' },
      { _global_context: true, _context_type: 'global', id: 'B' },
    ]);
  });

  it('should allow complex compositions of multiple Tracker instances and Configs', () => {
    const mainTrackerContexts: ContextsConfig = {
      locationStack: [
        { _location_context: true, _context_type: 'section', id: 'root' },
        { _location_context: true, _context_type: 'section', id: 'A' },
      ],
      globalContexts: [
        { _global_context: true, _context_type: 'global', id: 'X' },
        { _global_context: true, _context_type: 'global', id: 'Y' },
      ],
    };
    const mainTracker = new Tracker(mainTrackerContexts);

    // This new tracker is a clone of the mainTracker and extends it with two custom Contexts configuration
    const sectionTracker = new Tracker(
      mainTracker,
      {
        locationStack: [{ _location_context: true, _context_type: 'section', id: 'B' }],
        globalContexts: [{ _global_context: true, _context_type: 'global', id: 'Z' }],
      },
      {
        locationStack: [{ _location_context: true, _context_type: 'section', id: 'C' }],
      },
      // These last two configurations are useless, but we want to make sure nothing breaks with them
      {
        globalContexts: [],
      },
      {}
    );

    // The old tracker should be unaffected
    expect(mainTracker.locationStack).toEqual(mainTrackerContexts.locationStack);
    expect(mainTracker.globalContexts).toEqual(mainTrackerContexts.globalContexts);

    // The new Tracker, instead, should have all of the Contexts of the mainTracker + the extra Config provided
    expect(sectionTracker.locationStack).toEqual([
      { _location_context: true, _context_type: 'section', id: 'root' },
      { _location_context: true, _context_type: 'section', id: 'A' },
      { _location_context: true, _context_type: 'section', id: 'B' },
      { _location_context: true, _context_type: 'section', id: 'C' },
    ]);
    expect(sectionTracker.globalContexts).toEqual([
      { _global_context: true, _context_type: 'global', id: 'X' },
      { _global_context: true, _context_type: 'global', id: 'Y' },
      { _global_context: true, _context_type: 'global', id: 'Z' },
    ]);
  });

  describe('trackEvent', () => {
    const eventContexts: ContextsConfig = {
      locationStack: [
        { _location_context: true, _context_type: 'section', id: 'B' },
        { _location_context: true, _context_type: 'item', id: 'C' },
      ],
      globalContexts: [
        { _global_context: true, _context_type: 'global', id: 'W' },
        { _global_context: true, _context_type: 'global', id: 'X' },
      ],
    };
    const testEvent = new TrackerEvent(
      {
        event: 'test-event',
      },
      eventContexts
    );

    it('should merge Tracker Location Stack and Global Contexts with the Event ones', () => {
      const trackerContexts: ContextsConfig = {
        locationStack: [
          { _location_context: true, _context_type: 'section', id: 'root' },
          { _location_context: true, _context_type: 'section', id: 'A' },
        ],
        globalContexts: [
          { _global_context: true, _context_type: 'global', id: 'Y' },
          { _global_context: true, _context_type: 'global', id: 'Z' },
        ],
      };
      const testTracker = new Tracker(trackerContexts);
      expect(testEvent.locationStack).toStrictEqual(eventContexts.locationStack);
      expect(testEvent.globalContexts).toStrictEqual(eventContexts.globalContexts);
      const trackedEvent = testTracker.trackEvent(testEvent);
      expect(testEvent.locationStack).toStrictEqual(eventContexts.locationStack);
      expect(testEvent.globalContexts).toStrictEqual(eventContexts.globalContexts);
      expect(testTracker.locationStack).toStrictEqual(trackerContexts.locationStack);
      expect(testTracker.globalContexts).toStrictEqual(trackerContexts.globalContexts);
      expect(trackedEvent.locationStack).toStrictEqual([
        { _location_context: true, _context_type: 'section', id: 'root' },
        { _location_context: true, _context_type: 'section', id: 'A' },
        { _location_context: true, _context_type: 'section', id: 'B' },
        { _location_context: true, _context_type: 'item', id: 'C' },
      ]);
      expect(trackedEvent.globalContexts).toStrictEqual([
        { _global_context: true, _context_type: 'global', id: 'W' },
        { _global_context: true, _context_type: 'global', id: 'X' },
        { _global_context: true, _context_type: 'global', id: 'Y' },
        { _global_context: true, _context_type: 'global', id: 'Z' },
      ]);
    });

    it('should execute all plugins implementing the initialize callback', () => {
      const pluginC: TrackerPlugin = { pluginName: 'pluginC', initialize: jest.fn(noop) };
      const pluginD: TrackerPlugin = { pluginName: 'pluginD', initialize: jest.fn(noop) };
      const testTracker = new Tracker({ plugins: new TrackerPlugins([pluginC, pluginD]) });
      expect(pluginC.initialize).toHaveBeenCalledWith(testTracker);
      expect(pluginD.initialize).toHaveBeenCalledWith(testTracker);
    });

    it('should execute all plugins implementing the beforeTransport callback', () => {
      const pluginE: TrackerPlugin = { pluginName: 'pluginE', beforeTransport: jest.fn(noop) };
      const pluginF: TrackerPlugin = { pluginName: 'pluginF', beforeTransport: jest.fn(noop) };
      const testTracker = new Tracker({ plugins: new TrackerPlugins([pluginE, pluginF]) });
      testTracker.trackEvent(testEvent);
      expect(pluginE.beforeTransport).toHaveBeenCalledWith(testEvent);
      expect(pluginF.beforeTransport).toHaveBeenCalledWith(testEvent);
    });

    it('should send the Event via the given TrackerTransport', () => {
      const testTransport = new LogTransport();
      jest.spyOn(testTransport, 'handle');
      const testTracker = new Tracker({ transport: testTransport });
      testTracker.trackEvent(testEvent);
      expect(testTransport.handle).toHaveBeenCalledWith(testEvent);
    });

    it("should not send the Event via the given TrackerTransport if it's not usable", () => {
      const unusableTransport = new UnusableTransport();
      expect(unusableTransport.isUsable()).toEqual(false);
      jest.spyOn(unusableTransport, 'handle');
      const testTracker = new Tracker({ transport: unusableTransport });
      testTracker.trackEvent(testEvent);
      expect(unusableTransport.handle).not.toHaveBeenCalled();
    });
  });
});
