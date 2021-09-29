import { AbstractGlobalContext, AbstractLocationContext, Contexts } from '@objectiv/schema';
import { ApplicationContextPlugin } from './ApplicationContextPlugin';
import { ContextsConfig } from './Context';
import { TrackerEvent, TrackerEventConfig } from './TrackerEvent';
import { TrackerPlugins } from './TrackerPlugin';
import { TrackerTransport } from './TrackerTransport';

/**
 * The configuration of the Tracker
 */
export type TrackerConfig = ContextsConfig & {
  /**
   * Application ID. Used to generate ApplicationContext (global context)
   */
  applicationId: string;

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
 * The default list of Plugins of Web Tracker
 */
export const getDefaultTrackerPluginsList = (config: TrackerConfig) => [new ApplicationContextPlugin(config)];

/**
 * Our basic platform-agnostic JavaScript Tracker interface and implementation
 */
export class Tracker implements Contexts {
  readonly applicationId: string;
  readonly transport?: TrackerTransport;
  readonly plugins: TrackerPlugins;

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
  constructor(trackerConfig: TrackerConfig, ...contextConfigs: ContextsConfig[]) {
    this.applicationId = trackerConfig.applicationId;
    this.transport = trackerConfig.transport;
    this.plugins = trackerConfig.plugins ?? new TrackerPlugins(getDefaultTrackerPluginsList(trackerConfig));

    // Process ContextConfigs
    let new_location_stack: AbstractLocationContext[] = trackerConfig.location_stack ?? [];
    let new_global_contexts: AbstractGlobalContext[] = trackerConfig.global_contexts ?? [];
    contextConfigs.forEach(({ location_stack, global_contexts }) => {
      new_location_stack = [...new_location_stack, ...(location_stack ?? [])];
      new_global_contexts = [...new_global_contexts, ...(global_contexts ?? [])];
    });
    this.location_stack = new_location_stack;
    this.global_contexts = new_global_contexts;

    console.groupCollapsed(
      `｢objectiv:Tracker｣ Initialized ${
        this.location_stack.length
          ? '(' +
            this.location_stack.map((context) => `${context._type.replace('Context', '')}:${context.id}`).join(' > ') +
            ')'
          : ''
      }`
    );
    console.log(`Application ID: ${this.applicationId}`);
    console.log(`Transport: ${this.transport?.transportName ?? 'none'}`);
    console.group(`Plugins:`);
    console.log(this.plugins.list.map((plugin) => plugin.pluginName).join(', '));
    console.groupEnd();
    console.group(`Location Stack:`);
    console.log(this.location_stack);
    console.groupEnd();
    console.group(`Global Contexts:`);
    console.log(this.global_contexts);
    console.groupEnd();
    console.groupEnd();

    // Execute all plugins `initialize` callback. Plugins may use this to register automatic event listeners
    this.plugins.initialize(this);
  }

  /**
   * Merges Tracker Location and Global contexts, runs all Plugins and sends the Event via the TrackerTransport.
   */
  async trackEvent(event: TrackerEventConfig): Promise<TrackerEvent> {
    // TrackerEvent and Tracker share the ContextsConfig interface. We can combine them by creating a new TrackerEvent.
    const trackedEvent = new TrackerEvent(event, this);

    // Set tracking time
    trackedEvent.setTime();

    // Execute all plugins `beforeTransport` callback. Plugins may enrich or add Contexts to the TrackerEvent
    this.plugins.beforeTransport(trackedEvent);

    // Hand over TrackerEvent to TrackerTransport, if enabled and usable. They may send it, queue it, store it, etc
    if (this.transport && this.transport.isUsable()) {
      // istanbul ignore next
      console.groupCollapsed(
        `｢objectiv:Tracker｣ Tracking ${trackedEvent._type} ${
          this.location_stack.length
            ? '(' +
              this.location_stack
                .map((context) => `${context._type.replace('Context', '')}:${context.id}`)
                .join(' > ') +
              ')'
            : ''
        }`
      );
      console.log(`Event ID: ${trackedEvent.id}`);
      // istanbul ignore next
      console.log(`Time: ${trackedEvent.time ?? 'none'}`);
      console.group(`Location Stack:`);
      console.log(trackedEvent.location_stack);
      console.groupEnd();
      console.group(`Global Contexts:`);
      console.log(trackedEvent.global_contexts);
      console.groupEnd();
      console.groupEnd();

      await this.transport.handle(trackedEvent);
    }

    return trackedEvent;
  }
}
