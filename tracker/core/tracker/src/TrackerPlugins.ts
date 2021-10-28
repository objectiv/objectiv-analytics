import { Tracker } from './Tracker';
import { TrackerConsole } from './TrackerConsole';
import { TrackerEvent } from './TrackerEvent';
import { TrackerPluginConfig, TrackerPluginInterface } from './TrackerPluginInterface';
import { TrackerPluginLifecycleInterface } from './TrackerPluginLifecycleInterface';

/**
 * TrackerPlugins can be specified by instance, name or even on the fly as Objects.
 *
 * @example
 *
 *  Given a hypothetical PluginA:
 *
 *    class PluginA implements TrackerPlugin {
 *      readonly pluginName = 'pluginA';
 *      readonly parameter?: string;
 *
 *      constructor(args?: { parameter?: string }) {
 *        this.parameter = args?.parameter;
 *      }
 *
 *      isUsable() {
 *        return true;
 *      }
 *    }
 *
 *  And its factory:
 *
 *    const PluginAFactory = (parameter: string) => new PluginA({ parameter });
 *
 *  These would be all valid ways of adding it to the Plugins list:
 *
 *    PluginA
 *    new PluginA()
 *    new PluginA({ parameter: 'parameterValue' })
 *    PluginAFactory('parameterValue')
 *
 *  And it's also possible to define a Plugin on the fly as an Object:
 *
 *    {
 *      pluginName: 'pluginA',
 *      parameter: 'parameterValue',
 *      isUsable: () => true
 *    } as TrackerPlugin
 *
 */
export type TrackerPluginsConfiguration = TrackerPluginConfig & {
  plugins: TrackerPluginInterface[];
};

/**
 * TrackerPlugins is responsible for constructing TrackerPlugin instances and orchestrating their callbacks.
 * It also makes sure to check if Plugins are usable, before executing their callbacks.
 *
 * @note plugin order matters, as they are executed sequentially, a plugin executed later has access to previous
 * Plugins mutations. For example a plugin meant to access the finalized version of the TrackerEvent should be placed
 * at the bottom of the list.
 */
export class TrackerPlugins implements TrackerPluginLifecycleInterface {
  readonly console?: TrackerConsole;
  readonly plugins: TrackerPluginInterface[];

  /**
   * Plugins can be lazy. Map through them to instantiate them.
   */
  constructor(trackerPluginsConfig: TrackerPluginsConfiguration) {
    this.console = trackerPluginsConfig.console;
    this.plugins = trackerPluginsConfig.plugins;

    if (this.console) {
      this.console.groupCollapsed(`｢objectiv:TrackerPlugins｣ Initialized`);
      this.console.group(`Plugins:`);
      this.console.log(this.plugins.map((plugin) => plugin.pluginName).join(', '));
      this.console.groupEnd();
      this.console.groupEnd();
    }
  }

  /**
   * Calls each Plugin's `initialize` callback function, if defined
   */
  initialize(tracker: Tracker): void {
    this.plugins.forEach((plugin) => plugin.isUsable() && plugin.initialize && plugin.initialize(tracker));
  }

  /**
   * Calls each Plugin's `beforeTransport` callback function, if defined
   */
  beforeTransport(event: TrackerEvent): void {
    this.plugins.forEach((plugin) => plugin.isUsable() && plugin.beforeTransport && plugin.beforeTransport(event));
  }
}
