import { AbstractGlobalContext, AbstractLocationContext, Contexts } from '@objectiv/schema';
import { ApplicationContextPlugin } from './ApplicationContextPlugin';
import { ContextsConfig } from './Context';
import { waitForPromise } from './helpers';
import { TrackerConsole } from './TrackerConsole';
import { TrackerEvent, TrackerEventConfig } from './TrackerEvent';
import { TrackerPlugins } from './TrackerPlugins';
import { TrackerQueueInterface } from './TrackerQueueInterface';
import { TrackerTransportInterface } from './TrackerTransportInterface';

/**
 * The configuration of the Tracker
 */
export type TrackerConfig = ContextsConfig & {
  /**
   * Application ID. Used to generate ApplicationContext (global context).
   */
  applicationId: string;

  /**
   * Optional. Unique identifier for the TrackerInstance. Defaults to the same value of `applicationId`.
   */
  trackerId?: string;

  /**
   * Optional. TrackerQueue instance. Responsible for queueing and batching Events. Queuing occurs before Transport.
   */
  queue?: TrackerQueueInterface;

  /**
   * Optional. TrackerTransport instance. Responsible for sending or storing Events. Transport occurs after Queueing.
   */
  transport?: TrackerTransportInterface;

  /**
   * Optional. Plugins that will be executed when the Tracker initializes and before the Event is sent.
   */
  plugins?: TrackerPlugins;

  /**
   * Optional. A TrackerConsole instance for logging.
   */
  console?: TrackerConsole;

  /**
   * Optional. Determines if the TrackerInstance.trackEvent will process Events or not.
   */
  active?: boolean;
};

/**
 * The default list of Plugins of Web Tracker
 */
export const getDefaultTrackerPluginsList = (trackerConfig: TrackerConfig) => [
  new ApplicationContextPlugin({ applicationId: trackerConfig.applicationId, console: trackerConfig.console }),
];

/**
 * Our basic platform-agnostic JavaScript Tracker interface and implementation
 */
export class Tracker implements Contexts, TrackerConfig {
  readonly console?: TrackerConsole;
  readonly applicationId: string;
  readonly trackerId: string;
  readonly queue?: TrackerQueueInterface;
  readonly transport?: TrackerTransportInterface;
  readonly plugins: TrackerPlugins;

  active: boolean;

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
    this.console = trackerConfig.console;
    this.applicationId = trackerConfig.applicationId;
    this.trackerId = trackerConfig.trackerId ?? trackerConfig.applicationId;
    this.queue = trackerConfig.queue;
    this.transport = trackerConfig.transport;
    this.plugins =
      trackerConfig.plugins ??
      new TrackerPlugins({ console: trackerConfig.console, plugins: getDefaultTrackerPluginsList(trackerConfig) });

    // By default Tracker Instances are active
    this.active = trackerConfig.active ?? true;

    // Process ContextConfigs
    let new_location_stack: AbstractLocationContext[] = trackerConfig.location_stack ?? [];
    let new_global_contexts: AbstractGlobalContext[] = trackerConfig.global_contexts ?? [];
    contextConfigs.forEach(({ location_stack, global_contexts }) => {
      new_location_stack = [...new_location_stack, ...(location_stack ?? [])];
      new_global_contexts = [...new_global_contexts, ...(global_contexts ?? [])];
    });
    this.location_stack = new_location_stack;
    this.global_contexts = new_global_contexts;

    if (this.console) {
      this.console.groupCollapsed(
        `｢objectiv:Tracker:${this.trackerId}｣ Initialized (${this.location_stack
          .map((context) => `${context._type.replace('Context', '')}:${context.id}`)
          .join(' > ')})`
      );
      this.console.log(`Active: ${this.active}`);
      this.console.log(`Application ID: ${this.applicationId}`);
      this.console.log(`Queue: ${this.queue?.queueName ?? 'none'}`);
      this.console.log(`Transport: ${this.transport?.transportName ?? 'none'}`);
      this.console.group(`Plugins:`);
      this.console.log(this.plugins.plugins.map((plugin) => plugin.pluginName).join(', '));
      this.console.groupEnd();
      this.console.group(`Location Stack:`);
      this.console.log(this.location_stack);
      this.console.groupEnd();
      this.console.group(`Global Contexts:`);
      this.console.log(this.global_contexts);
      this.console.groupEnd();
      this.console.groupEnd();
    }

    // If active, initialize plugins and queue, if any
    if (this.active) {
      // Execute all plugins `initialize` callback. Plugins may use this to register automatic event listeners
      this.plugins.initialize(this);

      // If we have a Queue and a usable Transport, start Queue runner
      if (this.queue && this.transport && this.transport.isUsable()) {
        // Bind the handle function to its Transport instance to preserve its scope
        const processFunction = this.transport.handle.bind(this.transport);

        // Set the queue processFunction to transport.handle method: the queue will run Transport.handle for each batch
        this.queue.setProcessFunction(processFunction);

        // And start the Queue runner
        this.queue.startRunner();

        if (this.console) {
          this.console.log(
            `%c｢objectiv:Tracker:${this.trackerId}｣ ${this.queue.queueName} runner for ${this.transport.transportName} started`,
            'font-weight:bold'
          );
        }
      }
    }
  }

  /**
   * Setter for the Tracker Instance `active` state
   */
  setActive(newActiveState: boolean) {
    if (newActiveState !== this.active) {
      this.active = newActiveState;

      if (this.active) {
        this.plugins.initialize(this);
      }

      if (this.console) {
        this.console.log(
          `%c｢objectiv:Tracker:${this.trackerId}｣ New state: ${this.active ? 'active' : 'inactive'}`,
          'font-weight: bold'
        );
      }
    }
  }

  /**
   * Flushes the Queue
   */
  flushQueue() {
    if (this.queue) {
      this.queue.flush();
    }
  }

  /**
   * Waits for Queue `isIdle` in an attempt to wait for it to finish its job.
   * Resolves regardless if the Queue reaches an idle state or timeout is reached.
   */
  async waitForQueue(parameters?: { intervalMs?: number; timeoutMs?: number }): Promise<boolean> {
    if (this.queue) {
      // Some - hopefully - sensible defaults. 100ms for polling and double the Queue's batch delay as timeout.
      const intervalMs = parameters?.intervalMs ?? 100;
      const timeoutMs = parameters?.timeoutMs ?? this.queue.batchDelayMs * 2;

      // Bind the isHandle function to its Queue instance to preserve its scope
      const predicate = this.queue.isIdle.bind(this.queue);

      return waitForPromise({ predicate, intervalMs, timeoutMs });
    }
    return true;
  }

  /**
   * Merges Tracker Location and Global contexts, runs all Plugins and sends the Event via the TrackerTransport.
   */
  async trackEvent(event: TrackerEventConfig): Promise<TrackerEvent> {
    // TrackerEvent and Tracker share the ContextsConfig interface. We can combine them by creating a new TrackerEvent.
    const trackedEvent = new TrackerEvent(event, this);

    // Do nothing if the TrackerInstance is inactive
    if (!this.active) {
      return trackedEvent;
    }

    // Set tracking time
    trackedEvent.setTime();

    // Execute all plugins `beforeTransport` callback. Plugins may enrich or add Contexts to the TrackerEvent
    this.plugins.beforeTransport(trackedEvent);

    // Hand over TrackerEvent to TrackerTransport or TrackerQueue, if enabled and usable.
    if (this.transport && this.transport.isUsable()) {
      if (this.console) {
        this.console.groupCollapsed(
          `｢objectiv:Tracker:${this.trackerId}｣ ${this.queue ? 'Queuing' : 'Tracking'} ${
            trackedEvent._type
          } (${trackedEvent.location_stack
            .map((context) => `${context._type.replace('Context', '')}:${context.id}`)
            .join(' > ')})`
        );
        this.console.log(`Event ID: ${trackedEvent.id}`);
        this.console.log(`Time: ${trackedEvent.time}`);
        this.console.group(`Location Stack:`);
        this.console.log(trackedEvent.location_stack);
        this.console.groupEnd();
        this.console.group(`Global Contexts:`);
        this.console.log(trackedEvent.global_contexts);
        this.console.groupEnd();
        this.console.groupEnd();
      }

      if (this.queue) {
        await this.queue.push(trackedEvent);
      } else {
        await this.transport.handle(trackedEvent);
      }
    }

    return trackedEvent;
  }
}
