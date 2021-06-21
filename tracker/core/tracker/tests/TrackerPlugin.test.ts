import { TrackerEvent, TrackerPlugin, TrackerPlugins, TrackerPluginsConfiguration } from '../src';
import { noop } from './mocks';

describe('Plugin', () => {
  it('should instantiate when specifying an empty list of Plugins', () => {
    const testPlugins = new TrackerPlugins([]);
    expect(testPlugins).toBeInstanceOf(TrackerPlugins);
    expect(testPlugins).toEqual({ list: [] });
  });

  it('should instantiate when specifying a list of Plugins instances', () => {
    const plugins: TrackerPlugin[] = [{ pluginName: 'test-pluginA' }, { pluginName: 'test-pluginB' }];
    const testPlugins = new TrackerPlugins(plugins);
    expect(testPlugins).toBeInstanceOf(TrackerPlugins);
    expect(testPlugins).toEqual({ list: plugins });
  });

  it('should support Plugin creation via instance, class name, factory function or just plain object', () => {
    class TestPluginA implements TrackerPlugin {
      readonly pluginName = 'pluginA';
      readonly parameter?: string;

      constructor(args?: { parameter?: string }) {
        this.parameter = args?.parameter;
      }
    }
    const TestPluginAFactory = (parameter: string) => new TestPluginA({ parameter });
    const plugins: TrackerPluginsConfiguration = [
      new TestPluginA(),
      new TestPluginA({ parameter: 'parameterValue' }),
      TestPluginA,
      TestPluginAFactory('parameterValue'),
      {
        pluginName: 'pluginA',
        parameter: 'parameterValue',
      } as TrackerPlugin,
    ];
    const testPlugins = new TrackerPlugins(plugins);
    expect(testPlugins).toBeInstanceOf(TrackerPlugins);
    expect(testPlugins).toEqual({
      list: [
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
      ],
    });
  });

  it('should execute all Plugins implementing the `beforeTransport` callback', () => {
    const pluginA: TrackerPlugin = { pluginName: 'test-pluginA', beforeTransport: jest.fn(noop) };
    const pluginB: TrackerPlugin = { pluginName: 'test-pluginB', beforeTransport: jest.fn(noop) };
    const pluginC: TrackerPlugin = { pluginName: 'test-pluginC' };
    const plugins: TrackerPlugin[] = [pluginA, pluginB, pluginC];
    const testPlugins = new TrackerPlugins(plugins);
    expect(pluginA.beforeTransport).not.toHaveBeenCalled();
    expect(pluginB.beforeTransport).not.toHaveBeenCalled();
    const testEvent = new TrackerEvent({ event: 'test-event' });
    testPlugins.beforeTransport(testEvent);
    expect(pluginA.beforeTransport).toHaveBeenCalledWith(testEvent);
    expect(pluginB.beforeTransport).toHaveBeenCalledWith(testEvent);
  });
});
