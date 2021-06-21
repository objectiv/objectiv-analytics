import { AbstractEvent, AbstractGlobalContext, AbstractLocationContext, Contexts } from '@objectiv/schema';
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
  readonly location_stack: AbstractLocationContext[];
  readonly global_contexts: AbstractGlobalContext[];

  /**
   * Configures the Tracker instance via one TrackerConfig and optionally one or more ContextConfig.
   *
   * TrackerConfig is used to configure TrackerTransport and TrackerPlugins.
   *
   * ContextConfigs are used to configure location_stack and global_contexts. If multiple configurations have been
   * provided they will be merged onto each other to produce a single location_stack and global_contexts.
   */
  constructor(trackerConfig?: TrackerConfig, ...contextConfigs: ContextsConfig[]) {
    this.transport = trackerConfig?.transport;
    this.plugins = trackerConfig?.plugins;

    // Process ContextConfigs
    let new_location_stack: AbstractLocationContext[] = trackerConfig?.location_stack ?? [];
    let new_global_contexts: AbstractGlobalContext[] = trackerConfig?.global_contexts ?? [];
    contextConfigs.forEach(({ location_stack, global_contexts }) => {
      new_location_stack = [...new_location_stack, ...(location_stack ?? [])];
      new_global_contexts = [...new_global_contexts, ...(global_contexts ?? [])];
    });
    this.location_stack = new_location_stack;
    this.global_contexts = new_global_contexts;

    // Execute all plugins `initialize` callback. Plugins may use this to register automatic event listeners
    if (this.plugins) {
      this.plugins.initialize(this);
    }
  }

  /**
   * Merges Tracker Location and Global contexts, runs all Plugins and sends the Event via the TrackerTransport.
   */
  trackEvent(event: AbstractEvent): AbstractEvent {
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
