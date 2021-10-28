import { TrackerConsole } from './TrackerConsole';
import { TrackerPluginLifecycleInterface } from './TrackerPluginLifecycleInterface';

/**
 * The TrackerPluginConfig.
 */
export type TrackerPluginConfig = {
  /**
   * Optional. A TrackerConsole instance for logging.
   */
  console?: TrackerConsole;
};

/**
 * A TrackerPlugin must define its own `pluginName` and may define TrackerPluginLifecycle callbacks.
 * It also defines a method to determine if the plugin can be used. Similarly to the Transport interface, this can
 * be used to check environment requirements, APIs availability, etc.
 */
export interface TrackerPluginInterface extends TrackerPluginLifecycleInterface {
  readonly console?: TrackerConsole;
  readonly pluginName: string;

  /**
   * Should return if the TrackerPlugin can be used. Eg: a browser based plugin may want to return `false` during SSR.
   */
  isUsable(): boolean;
}

/**
 * The TrackerPlugin constructor interface.
 */
export interface TrackerPluginConstructor {
  new (pluginConfig: TrackerPluginConfig): TrackerPluginInterface;
}
