import { DeviceContext } from '@objectiv/schema';
import {
  makeDeviceContext,
  TrackerConsole,
  TrackerEvent,
  TrackerPluginConfig,
  TrackerPluginInterface,
} from '@objectiv/tracker-core';

/**
 * The WebDeviceContext Plugin gathers the current user-agent using the Navigator API.
 * It detects it during construction and adds it as GlobalContext before events are handed over to TrackerTransport.
 */
export class WebDeviceContextPlugin implements TrackerPluginInterface {
  readonly console?: TrackerConsole;
  readonly pluginName = `WebDeviceContextPlugin`;
  readonly webDeviceContext: DeviceContext;

  /**
   * Detects user-agent and generates a WebDeviceContext.
   */
  constructor(config?: TrackerPluginConfig) {
    this.console = config?.console;
    this.webDeviceContext = makeDeviceContext({
      id: 'device',
      user_agent: this.isUsable() ? navigator.userAgent : 'unknown',
    });

    if (this.console) {
      this.console.groupCollapsed(`｢objectiv:${this.pluginName}｣ Initialized`);
      this.console.group(`Device Context:`);
      this.console.log(this.webDeviceContext);
      this.console.groupEnd();
      this.console.groupEnd();
    }
  }

  /**
   * Add the the WebDeviceContext to the Event's Global Contexts
   */
  beforeTransport(event: TrackerEvent): void {
    event.global_contexts.push(this.webDeviceContext);
  }

  /**
   * Make this plugin usable only if the Navigator API is available
   */
  isUsable(): boolean {
    return typeof navigator !== 'undefined';
  }
}
