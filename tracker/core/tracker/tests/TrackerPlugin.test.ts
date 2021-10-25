import { TrackerEvent, TrackerPluginInterface, TrackerPlugins, TrackerPluginsConfiguration } from '../src';

describe('Plugin', () => {
  it('should instantiate when specifying an empty list of Plugins', () => {
    const testPlugins = new TrackerPlugins({ plugins: [] });
    expect(testPlugins).toBeInstanceOf(TrackerPlugins);
    expect(testPlugins).toEqual({ plugins: [] });
  });

  it('should instantiate when specifying a list of Plugins instances', () => {
    const plugins: TrackerPluginInterface[] = [
      { pluginName: 'test-pluginA', isUsable: () => true },
      { pluginName: 'test-pluginB', isUsable: () => true },
    ];
    const testPlugins = new TrackerPlugins({ plugins });
    expect(testPlugins).toBeInstanceOf(TrackerPlugins);
    expect(testPlugins).toEqual({ plugins });
  });

  it('should support Plugin creation via instance, class name, factory function or just plain object', () => {
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
    const TestPluginAFactory = (parameter: string) => new TestPluginA({ parameter });
    const plugins: TrackerPluginsConfiguration = {
      plugins: [
        new TestPluginA(),
        new TestPluginA({ parameter: 'parameterValue' }),
        TestPluginAFactory('parameterValue'),
        {
          pluginName: 'pluginA',
          parameter: 'parameterValue',
          isUsable: () => true,
        } as TrackerPluginInterface,
      ],
    };
    const testPlugins = new TrackerPlugins(plugins);
    expect(testPlugins).toBeInstanceOf(TrackerPlugins);
    expect(testPlugins).toEqual({
      plugins: [
        {
          pluginName: 'pluginA',
          parameter: undefined,
        },
        {
          pluginName: 'pluginA',
          parameter: 'parameterValue',
        },
        {
          pluginName: 'pluginA',
          parameter: 'parameterValue',
        },
        {
          pluginName: 'pluginA',
          parameter: 'parameterValue',
          isUsable: expect.any(Function),
        },
      ],
    });
  });

  it('should execute all Plugins implementing the `beforeTransport` callback', () => {
    const pluginA: TrackerPluginInterface = {
      pluginName: 'pluginA',
      isUsable: () => true,
      beforeTransport: jest.fn(),
    };
    const pluginB: TrackerPluginInterface = {
      pluginName: 'pluginB',
      isUsable: () => true,
      beforeTransport: jest.fn(),
    };
    const pluginC: TrackerPluginInterface = { pluginName: 'pluginC', isUsable: () => true };
    const plugins: TrackerPluginInterface[] = [pluginA, pluginB, pluginC];
    const testPlugins = new TrackerPlugins({ plugins });
    expect(pluginA.beforeTransport).not.toHaveBeenCalled();
    expect(pluginB.beforeTransport).not.toHaveBeenCalled();
    const testEvent = new TrackerEvent({ _type: 'test-event' });
    testPlugins.beforeTransport(testEvent);
    expect(pluginA.beforeTransport).toHaveBeenCalledWith(testEvent);
    expect(pluginB.beforeTransport).toHaveBeenCalledWith(testEvent);
  });

  it('should execute only Plugins that are usable', () => {
    const pluginA: TrackerPluginInterface = {
      pluginName: 'pluginA',
      isUsable: () => true,
      beforeTransport: jest.fn(),
    };
    const pluginB: TrackerPluginInterface = {
      pluginName: 'test-pluginB',
      isUsable: () => false,
      beforeTransport: jest.fn(),
    };
    const pluginC: TrackerPluginInterface = {
      pluginName: 'pluginC',
      isUsable: () => true,
      beforeTransport: jest.fn(),
    };
    const plugins: TrackerPluginInterface[] = [pluginA, pluginB, pluginC];
    const testPlugins = new TrackerPlugins({ plugins });
    expect(pluginA.beforeTransport).not.toHaveBeenCalled();
    expect(pluginB.beforeTransport).not.toHaveBeenCalled();
    expect(pluginC.beforeTransport).not.toHaveBeenCalled();
    const testEvent = new TrackerEvent({ _type: 'test-event' });
    testPlugins.beforeTransport(testEvent);
    expect(pluginA.beforeTransport).toHaveBeenCalledWith(testEvent);
    expect(pluginB.beforeTransport).not.toHaveBeenCalled();
    expect(pluginC.beforeTransport).toHaveBeenCalledWith(testEvent);
  });
});
