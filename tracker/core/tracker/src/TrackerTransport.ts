import { TrackerEvent } from './TrackerEvent';
import { TrackerQueue } from './TrackerQueue';

/**
 * The TrackerTransport interface provides a single function to handle one or more TrackerEvents.
 *
 * TrackerTransport implementations may vary depending on platform. Eg: web: fetch, node: https module, etc
 *
 * Also, simpler implementations can synchronously send TrackerEvents right away to the Collector while more complex
 * ones may leverage Queues, Workers and Storage for asynchronous sending, or batching.
 */
export interface TrackerTransport {
  /**
   * A name describing the Transport implementation for debugging purposes
   */
  readonly transportName: string;

  /**
   * Should return if the TrackerTransport can be used. Most useful in combination with TransportSwitch.
   */
  isUsable(): boolean;

  /**
   * Process one or more TrackerEvents. Eg. Send, queue, store, etc
   */
  handle(...args: [TrackerEvent, ...TrackerEvent[]]): void;
}

/**
 * TransportSwitch provides a fallback mechanism to pick the first usable transport in a list of them.
 * The switch is usable if at least one of the given TrackerTransports is usable.
 *
 * This mechanism can be used to configure multiple TrackerTransport instances, in order of preference, and
 * have TransportSwitch test each of them via the `isUsable` method to determine the topmost usable one.
 */
export class TransportSwitch implements TrackerTransport {
  readonly transportName = 'TransportSwitch';
  readonly firstUsableTransport?: TrackerTransport;

  /**
   * Finds the first TrackerTransport which `isUsable()`.
   */
  constructor(...args: [TrackerTransport, TrackerTransport, ...TrackerTransport[]]) {
    this.firstUsableTransport = args.find((trackerTransport) => trackerTransport.isUsable());
  }

  /**
   * Simply proxy the `handle` method to the usable TrackerTransport we found during construction, if any
   */
  handle(...args: [TrackerEvent, ...TrackerEvent[]]): void {
    if (!this.firstUsableTransport) {
      throw new Error(`${this.transportName}: no usable Transport found; make sure to verify usability first.`);
    }

    this.firstUsableTransport.handle(...args);
  }

  /**
   * The whole TransportSwitch is usable if we found a usable TrackerTransport
   */
  isUsable(): boolean {
    return Boolean(this.firstUsableTransport);
  }
}

/**
 * TransportGroup provides a mechanism to hand over TrackerEvents to multiple transports. The group is usable
 * if at least one of the given TrackerTransports is usable.
 *
 * This can be used when having multiple Collectors but also for simpler development needs, such as handling & logging
 */
export class TransportGroup implements TrackerTransport {
  readonly transportName = 'TransportGroup';
  readonly usableTransports: TrackerTransport[];

  /**
   * Filter and store the list of usable transports, received as construction parameters, in state
   */
  constructor(...args: [TrackerTransport, TrackerTransport, ...TrackerTransport[]]) {
    this.usableTransports = args.filter((transport) => transport.isUsable());
  }

  /**
   * Simply proxy the `handle` method to all the usable TrackerTransport instances we have.
   */
  handle(...args: [TrackerEvent, ...TrackerEvent[]]): void {
    if (!this.usableTransports.length) {
      throw new Error(`${this.transportName}: no usable Transports found; make sure to verify usability first.`);
    }

    this.usableTransports.map((transport) => transport.handle(...args));
  }

  /**
   * The whole TransportGroup is usable if we found at least one usable TrackerTransport
   */
  isUsable(): boolean {
    return Boolean(this.usableTransports.length);
  }
}

/**
 * The configuration object of a QueuedTransport. Requires a Queue and Transport instances.
 */
export type QueuedTransportConfig = {
  queue: TrackerQueue;
  transport: TrackerTransport;
};

/**
 * A TrackerTransport implementation that leverages TrackerQueue to handle events.
 * The queue runner is executed at construction. It's a simplistic implementation for now, just to test the concept.
 */
export class QueuedTransport implements TrackerTransport {
  readonly transportName = 'QueuedTransport';
  readonly transport: TrackerTransport;
  readonly queue: TrackerQueue;

  constructor(config: QueuedTransportConfig) {
    this.transport = config.transport;
    this.queue = config.queue;

    if (this.isUsable()) {
      // Start the queue runner. Each tick it will hand over a batch of TrackerEvents to the TrackerTransport
      this.queue.run(
        // Make sure to bind the `handle` method to its instance to preserve its scope
        this.transport.handle.bind(this.transport)
      );
    }
  }

  handle(...args: [TrackerEvent, ...TrackerEvent[]]): void {
    this.queue.enqueue(...args);
  }

  isUsable(): boolean {
    return this.transport.isUsable();
  }
}
