import { TrackerEvent } from './TrackerEvent';
import { Newable } from './helpers';
import { Tracker } from './Tracker';

/**
 * All possible callbacks of a TrackerPlugin.
 */
export interface PluginCallbacks {
  /**
   * Executed when the Tracker initializes.
   * Useful to register event listeners that execute autonomously. Eg: URLChangeEvent
   */
  initialize?: (tracker: Tracker) => void;

  /**
   * Executed before the TrackerEvent is handed over to the TrackerTransport.
   * Useful to gather Contexts that may have changed from the last TrackerEvent tracking. Eg: URL, Time, User, etc
   */
  beforeTransport?: (event: TrackerEvent) => void;
}

/**
 * A TrackerPlugin must define its own `pluginName` and may define PluginCallbacks callbacks.
 * It also defines a method to determine if the plugin can be used. Similarly to the Transport interface, this can
 * be used to check environment requirements, APIs availability, etc.
 */
export interface TrackerPlugin extends PluginCallbacks {
  readonly pluginName: string;

  /**
   * Should return if the TrackerPlugin can be used. Eg: a browser based plugin may want to return `false` during SSR.
   */
  isUsable(): boolean;
}

/**
 * TrackerPlugins can be specified by instance, name or even on the fly as Objects.
 *
 * TODO add support for functions when TS fixes this: https://github.com/microsoft/TypeScript/issues/37663
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
export type TrackerPluginsConfiguration = (TrackerPlugin | Newable<TrackerPlugin>)[];

/**
 * TrackerPlugins is responsible for constructing TrackerPlugin instances and orchestrating their callbacks.
 * It also makes sure to check if Plugins are usable, before executing their callbacks.
 *
 * @note plugin order matters, as they are executed sequentially, a plugin executed later has access to previous
 * Plugins mutations. For example a plugin meant to access the finalized version of the TrackerEvent should be placed
 * at the bottom of the list.
 */
export class TrackerPlugins implements PluginCallbacks {
  readonly list: TrackerPlugin[];

  /**
   * Plugins can be lazy. Map through them to instantiate them.
   */
  constructor(plugins: TrackerPluginsConfiguration) {
    this.list = plugins.map((plugin) => (typeof plugin === 'object' ? plugin : new plugin()));

    console.groupCollapsed(`｢objectiv:TrackerPlugins｣ Initialized`);
    console.group(`Plugins:`);
    console.log(this.list.map((plugin) => plugin.pluginName).join(', '));
    console.groupEnd();
    console.groupEnd();
  }

  /**
   * Calls each Plugin's `initialize` callback function, if defined
   */
  initialize(tracker: Tracker): void {
    this.list.forEach((plugin) => plugin.isUsable() && plugin.initialize && plugin.initialize(tracker));
  }

  /**
   * Calls each Plugin's `beforeTransport` callback function, if defined
   */
  beforeTransport(event: TrackerEvent): void {
    this.list.forEach((plugin) => plugin.isUsable() && plugin.beforeTransport && plugin.beforeTransport(event));
  }
}
