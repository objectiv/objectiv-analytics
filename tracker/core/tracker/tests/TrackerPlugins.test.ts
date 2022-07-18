/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { expectToThrow, MockConsoleImplementation } from '@objectiv/testing-tools';
import { generateGUID, Tracker, TrackerEvent, TrackerPluginInterface, TrackerPlugins } from '../src';

require('@objectiv/developer-tools');
globalThis.objectiv.devTools?.TrackerConsole.setImplementation(MockConsoleImplementation);

describe('Plugin', () => {
  beforeEach(() => {
    jest.resetAllMocks();
  });

  const tracker = new Tracker({ applicationId: 'test-tracker' });

  it('should instantiate when specifying an empty list of Plugins', () => {
    const testPlugins = new TrackerPlugins({ tracker, plugins: [] });
    expect(testPlugins).toBeInstanceOf(TrackerPlugins);
    expect(testPlugins).toEqual({ tracker, plugins: [] });
  });

  it('should instantiate when specifying a list of Plugins instances', () => {
    const plugins: TrackerPluginInterface[] = [
      { pluginName: 'test-pluginA', isUsable: () => true },
      { pluginName: 'test-pluginB', isUsable: () => true },
    ];
    const testPlugins = new TrackerPlugins({ tracker, plugins });
    expect(testPlugins).toBeInstanceOf(TrackerPlugins);
    expect(testPlugins).toEqual({ tracker, plugins });
  });

  it('should replace Plugins with the same name and use the last instance in the plugin list', () => {
    class TestPluginA implements TrackerPluginInterface {
      readonly pluginName = 'pluginA';
      readonly parameter?: string;

      constructor(args?: { parameter?: string }) {
        this.parameter = args?.parameter;
      }

      isUsable() {
        return true;
      }
    }
    const trackerPlugins = new TrackerPlugins({
      tracker,
      plugins: [new TestPluginA(), new TestPluginA({ parameter: 'parameterValue1' })],
    });

    expect(trackerPlugins.get('pluginA')).toEqual({
      pluginName: 'pluginA',
      parameter: 'parameterValue1',
    });
  });

  it('should return false if a plugin does not exist', () => {
    const pluginA = { pluginName: 'test-pluginA', isUsable: () => true };
    const pluginB = { pluginName: 'test-pluginB', isUsable: () => true };
    const testPlugins = new TrackerPlugins({ tracker, plugins: [pluginA, pluginB] });
    expect(testPlugins.has('test-pluginA')).toBe(true);
    expect(testPlugins.has('test-pluginB')).toBe(true);
    expect(testPlugins.has('test-pluginC')).toBe(false);
  });

  it('should get a plugin by its name or return null', () => {
    const pluginA = { pluginName: 'test-pluginA', isUsable: () => true };
    const pluginB = { pluginName: 'test-pluginB', isUsable: () => true };
    const testPlugins = new TrackerPlugins({ tracker, plugins: [pluginA, pluginB] });
    expect(testPlugins.get('test-pluginA')).toBe(pluginA);
    expect(testPlugins.get('test-pluginB')).toBe(pluginB);
    expectToThrow(() => testPlugins.get('test-pluginC'), '｢objectiv:TrackerPlugins｣ test-pluginC: not found');
  });

  it('should add plugins', () => {
    const pluginA = { pluginName: 'test-pluginA', isUsable: () => true, initialize: jest.fn() };
    const pluginB = { pluginName: 'test-pluginB', isUsable: () => true };
    const pluginC = { pluginName: 'test-pluginC', isUsable: () => true };
    const testPlugins = new TrackerPlugins({ tracker, plugins: [] });
    jest.resetAllMocks();
    testPlugins.add(pluginA);
    expect(pluginA.initialize).toHaveBeenCalledTimes(1);
    testPlugins.add(pluginB);
    expect(MockConsoleImplementation.log).toHaveBeenCalledTimes(2);
    expect(MockConsoleImplementation.log).toHaveBeenNthCalledWith(
      1,
      '%c｢objectiv:TrackerPlugins｣ test-pluginA added at index 0',
      'font-weight: bold'
    );
    expect(MockConsoleImplementation.log).toHaveBeenNthCalledWith(
      2,
      '%c｢objectiv:TrackerPlugins｣ test-pluginB added at index 1',
      'font-weight: bold'
    );
    expectToThrow(
      () => testPlugins.add(pluginB),
      '｢objectiv:TrackerPlugins｣ test-pluginB: already exists. Use "replace" instead'
    );
    expect(testPlugins.plugins).toEqual([
      {
        initialize: expect.any(Function),
        isUsable: expect.any(Function),
        pluginName: 'test-pluginA',
      },
      {
        isUsable: expect.any(Function),
        pluginName: 'test-pluginB',
      },
    ]);
    testPlugins.add(pluginC, 1);
    expect(testPlugins.plugins).toEqual([
      {
        initialize: expect.any(Function),
        isUsable: expect.any(Function),
        pluginName: 'test-pluginA',
      },
      {
        isUsable: expect.any(Function),
        pluginName: 'test-pluginC',
      },
      {
        isUsable: expect.any(Function),
        pluginName: 'test-pluginB',
      },
    ]);
    expectToThrow(() => testPlugins.add(pluginC, -1), '｢objectiv:TrackerPlugins｣ invalid index');
    expectToThrow(() => testPlugins.add(pluginC, Infinity), '｢objectiv:TrackerPlugins｣ invalid index');
    // @ts-ignore
    expectToThrow(() => testPlugins.add(pluginC, '0'), '｢objectiv:TrackerPlugins｣ invalid index');
  });

  it('should remove plugins', () => {
    const pluginA = { pluginName: 'test-pluginA', isUsable: () => true };
    const pluginB = { pluginName: 'test-pluginB', isUsable: () => true };
    const pluginC = { pluginName: 'test-pluginC', isUsable: () => true };
    const testPlugins = new TrackerPlugins({ tracker, plugins: [pluginA, pluginB, pluginC] });
    jest.resetAllMocks();
    testPlugins.remove('test-pluginB');
    expect(MockConsoleImplementation.log).toHaveBeenCalledTimes(1);
    expect(MockConsoleImplementation.log).toHaveBeenNthCalledWith(
      1,
      '%c｢objectiv:TrackerPlugins｣ test-pluginB removed',
      'font-weight: bold'
    );
    expect(testPlugins.plugins).toEqual([
      {
        isUsable: expect.any(Function),
        pluginName: 'test-pluginA',
      },
      {
        isUsable: expect.any(Function),
        pluginName: 'test-pluginC',
      },
    ]);
    expectToThrow(() => testPlugins.remove('test-pluginB'), '｢objectiv:TrackerPlugins｣ test-pluginB: not found');
  });

  it('should replace plugins', () => {
    const pluginA = { pluginName: 'test-pluginA', isUsable: () => true, parameterA: false };
    const pluginB = { pluginName: 'test-pluginB', isUsable: () => true, parameterB: false };
    const pluginC = { pluginName: 'test-pluginC', isUsable: () => true, parameterC: false };
    const testPlugins = new TrackerPlugins({ tracker, plugins: [pluginA, pluginB, pluginC] });
    expect(testPlugins.plugins).toEqual([
      {
        parameterA: false,
        isUsable: expect.any(Function),
        pluginName: 'test-pluginA',
      },
      {
        parameterB: false,
        isUsable: expect.any(Function),
        pluginName: 'test-pluginB',
      },
      {
        parameterC: false,
        isUsable: expect.any(Function),
        pluginName: 'test-pluginC',
      },
    ]);
    const existingPlugin = testPlugins.get('test-pluginB');
    if (!existingPlugin) {
      throw new Error('test-pluginB Plugin not found');
    }
    const newPluginB1 = { ...existingPlugin, parameterB: true, initialize: jest.fn() };
    jest.resetAllMocks();
    testPlugins.replace(newPluginB1);
    expect(newPluginB1.initialize).toHaveBeenCalledTimes(1);
    expect(MockConsoleImplementation.log).toHaveBeenCalledTimes(2);
    expect(MockConsoleImplementation.log).toHaveBeenNthCalledWith(
      1,
      '%c｢objectiv:TrackerPlugins｣ test-pluginB removed',
      'font-weight: bold'
    );
    expect(MockConsoleImplementation.log).toHaveBeenNthCalledWith(
      2,
      '%c｢objectiv:TrackerPlugins｣ test-pluginB added at index 1',
      'font-weight: bold'
    );
    expect(testPlugins.plugins).toEqual([
      {
        parameterA: false,
        isUsable: expect.any(Function),
        pluginName: 'test-pluginA',
      },
      {
        parameterB: true,
        initialize: expect.any(Function),
        isUsable: expect.any(Function),
        pluginName: 'test-pluginB',
      },
      {
        parameterC: false,
        isUsable: expect.any(Function),
        pluginName: 'test-pluginC',
      },
    ]);
    const newPluginD = { pluginName: 'test-pluginD', isUsable: () => true };
    expectToThrow(() => testPlugins.replace(newPluginD), '｢objectiv:TrackerPlugins｣ test-pluginD: not found');
    const newPluginB2 = { pluginName: 'test-pluginB', isUsable: () => true, newParameter: { a: 1 } };
    testPlugins.replace(newPluginB2, 0);
    expect(testPlugins.plugins).toEqual([
      {
        isUsable: expect.any(Function),
        newParameter: { a: 1 },
        pluginName: 'test-pluginB',
      },
      {
        parameterA: false,
        isUsable: expect.any(Function),
        pluginName: 'test-pluginA',
      },
      {
        parameterC: false,
        isUsable: expect.any(Function),
        pluginName: 'test-pluginC',
      },
    ]);
    expectToThrow(() => testPlugins.replace(newPluginB2, -1), '｢objectiv:TrackerPlugins｣ invalid index');
    expectToThrow(() => testPlugins.replace(newPluginB2, Infinity), '｢objectiv:TrackerPlugins｣ invalid index');
    // @ts-ignore
    expectToThrow(() => testPlugins.replace(newPluginB2, '0'), '｢objectiv:TrackerPlugins｣ invalid index');
  });

  it('constructor should behave like `add`', () => {
    class TestPluginA implements TrackerPluginInterface {
      readonly pluginName = 'pluginA';
      readonly parameter?: string;

      constructor(args?: { parameter?: string }) {
        this.parameter = args?.parameter;
      }

      isUsable() {
        return true;
      }
    }
    const trackerPlugins = new TrackerPlugins({
      tracker,
      plugins: [new TestPluginA(), new TestPluginA({ parameter: 'parameterValue1' })],
    });

    expect(trackerPlugins.get('pluginA')).toEqual({
      pluginName: 'pluginA',
      parameter: 'parameterValue1',
    });
  });

  it('should execute all Plugins implementing the `enrich` callback', () => {
    const pluginA: TrackerPluginInterface = {
      pluginName: 'pluginA',
      isUsable: () => true,
      enrich: jest.fn(),
    };
    const pluginB: TrackerPluginInterface = {
      pluginName: 'pluginB',
      isUsable: () => true,
      enrich: jest.fn(),
    };
    const pluginC: TrackerPluginInterface = { pluginName: 'pluginC', isUsable: () => true };
    const plugins: TrackerPluginInterface[] = [pluginA, pluginB, pluginC];
    const testPlugins = new TrackerPlugins({ tracker, plugins });
    expect(pluginA.enrich).not.toHaveBeenCalled();
    expect(pluginB.enrich).not.toHaveBeenCalled();
    const testEvent = new TrackerEvent({ _type: 'test-event', id: generateGUID(), time: Date.now() });
    testPlugins.enrich(testEvent);
    expect(pluginA.enrich).toHaveBeenCalledWith(testEvent);
    expect(pluginB.enrich).toHaveBeenCalledWith(testEvent);
  });

  it('should execute all Plugins implementing the `validate` callback', () => {
    const pluginA: TrackerPluginInterface = {
      pluginName: 'pluginA',
      isUsable: () => true,
      validate: jest.fn(),
    };
    const pluginB: TrackerPluginInterface = {
      pluginName: 'pluginB',
      isUsable: () => true,
      validate: jest.fn(),
    };
    const pluginC: TrackerPluginInterface = { pluginName: 'pluginC', isUsable: () => true };
    const plugins: TrackerPluginInterface[] = [pluginA, pluginB, pluginC];
    const testPlugins = new TrackerPlugins({ tracker, plugins });
    expect(pluginA.validate).not.toHaveBeenCalled();
    expect(pluginB.validate).not.toHaveBeenCalled();
    const testEvent = new TrackerEvent({ _type: 'test-event', id: generateGUID(), time: Date.now() });
    testPlugins.validate(testEvent);
    expect(pluginA.validate).toHaveBeenCalledWith(testEvent);
    expect(pluginB.validate).toHaveBeenCalledWith(testEvent);
  });

  it('should execute only Plugins that are usable', () => {
    const pluginA: TrackerPluginInterface = {
      pluginName: 'pluginA',
      isUsable: () => true,
      enrich: jest.fn(),
    };
    const pluginB: TrackerPluginInterface = {
      pluginName: 'test-pluginB',
      isUsable: () => false,
      enrich: jest.fn(),
    };
    const pluginC: TrackerPluginInterface = {
      pluginName: 'pluginC',
      isUsable: () => true,
      enrich: jest.fn(),
    };
    const plugins: TrackerPluginInterface[] = [pluginA, pluginB, pluginC];
    const testPlugins = new TrackerPlugins({ tracker, plugins });
    expect(pluginA.enrich).not.toHaveBeenCalled();
    expect(pluginB.enrich).not.toHaveBeenCalled();
    expect(pluginC.enrich).not.toHaveBeenCalled();
    const testEvent = new TrackerEvent({ _type: 'test-event', id: generateGUID(), time: Date.now() });
    testPlugins.enrich(testEvent);
    expect(pluginA.enrich).toHaveBeenCalledWith(testEvent);
    expect(pluginB.enrich).not.toHaveBeenCalled();
    expect(pluginC.enrich).toHaveBeenCalledWith(testEvent);
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

    it('should add plugins without logging', () => {
      const pluginA = { pluginName: 'test-pluginA', isUsable: () => true, initialize: jest.fn() };
      const pluginB = { pluginName: 'test-pluginB', isUsable: () => true };
      const testPlugins = new TrackerPlugins({ tracker, plugins: [] });
      jest.resetAllMocks();
      testPlugins.add(pluginA);
      expect(pluginA.initialize).toHaveBeenCalledTimes(1);
      testPlugins.add(pluginB);
      expect(MockConsoleImplementation.log).not.toHaveBeenCalled();
    });

    it('should remove plugins without logging', () => {
      const pluginA = { pluginName: 'test-pluginA', isUsable: () => true };
      const pluginB = { pluginName: 'test-pluginB', isUsable: () => true };
      const pluginC = { pluginName: 'test-pluginC', isUsable: () => true };
      const testPlugins = new TrackerPlugins({ tracker, plugins: [pluginA, pluginB, pluginC] });
      jest.resetAllMocks();
      testPlugins.remove('test-pluginB');
      expect(MockConsoleImplementation.log).not.toHaveBeenCalled();
    });
  });
});
