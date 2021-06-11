import { AbstractGlobalContext, AbstractLocationContext, Contexts } from '@objectiv/schema';
import { ContextsConfig } from './Context';
import { TrackerEvent } from './TrackerEvent';
import { TrackerPlugins } from './TrackerPlugin';
import { TrackerTransport } from './TrackerTransport';

/**
 * The configuration of the Tracker
 */
export type TrackerConfig = ContextsConfig & {
  /**
   * Optional. TrackerTransport instance. Responsible for sending or storing Events.
   */
  transport?: TrackerTransport;

  /**
   * Optional. Plugins that will be executed when the Tracker initializes and before the Event is sent.
   */
  plugins?: TrackerPlugins;
};

/**
 * Our basic platform-agnostic JavaScript Tracker interface and implementation
 */
export class Tracker implements Contexts {
  readonly transport?: TrackerTransport;
  readonly plugins?: TrackerPlugins;

  // Contexts interface
  readonly locationStack: AbstractLocationContext[];
  readonly globalContexts: AbstractGlobalContext[];

  /**
   * Configures the Tracker instance via one TrackerConfig and optionally one or more ContextConfig.
   *
   * TrackerConfig is used to configure TrackerTransport and TrackerPlugins.
   *
   * ContextConfigs are used to configure LocationStack and GlobalContexts. If multiple configurations have been
   * provided they will be merged onto each other to produce a single LocationStack and GlobalContexts.
   */
  constructor(trackerConfig?: TrackerConfig, ...contextConfigs: ContextsConfig[]) {
    this.transport = trackerConfig?.transport;
    this.plugins = trackerConfig?.plugins;

    // Process ContextConfigs
    let newLocationStack: AbstractLocationContext[] = trackerConfig?.locationStack ?? [];
    let newGlobalContexts: AbstractGlobalContext[] = trackerConfig?.globalContexts ?? [];
    contextConfigs.forEach(({ locationStack, globalContexts }) => {
      newLocationStack = [...newLocationStack, ...(locationStack ?? [])];
      newGlobalContexts = [...newGlobalContexts, ...(globalContexts ?? [])];
    });
    this.locationStack = newLocationStack;
    this.globalContexts = newGlobalContexts;

    // Execute all plugins `initialize` callback. Plugins may use this to register automatic event listeners
    if (this.plugins) {
      this.plugins.initialize(this);
    }
  }

  /**
   * Merges Tracker Location and Global contexts, runs all Plugins and sends the Event via the TrackerTransport.
   */
  trackEvent(event: TrackerEvent): TrackerEvent {
    // TrackerEvent and Tracker share the ContextsConfig interface. We can combine them by creating a new TrackerEvent.
    const eventToTrack = new TrackerEvent(event, this);

    // Execute all plugins `beforeTransport` callback. Plugins may enrich or add Contexts to the TrackerEvent
    if (this.plugins) {
      this.plugins.beforeTransport(eventToTrack);
    }

    // Hand over TrackerEvent to TrackerTransport, if enabled and usable. They may send it, queue it, store it, etc
    if (this.transport && this.transport.isUsable()) {
      this.transport.handle(eventToTrack);
    }

    return eventToTrack;
  }
}
