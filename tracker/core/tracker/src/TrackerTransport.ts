import ExtendableError from 'es6-error';
import { isNonEmptyArray, NonEmptyArray } from './helpers';
import { TrackerEvent } from './TrackerEvent';
import { TrackerQueue } from './TrackerQueue';

/**
 * TrackerTransports can receive either Events ready to be processed or Event Promises.
 */
export type TransportableEvent = TrackerEvent | Promise<TrackerEvent>;

/**
 * A custom error thrown by Sending Transports (eg: Fetch) whenever the Collector was not reachable.
 * RetryTransportAttempts will react to it by retrying.
 */
export class TransportSendError extends ExtendableError {}

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
   * Process one or more TransportableEvent. Eg. Send, queue, store, etc
   */
  handle(...args: NonEmptyArray<TransportableEvent>): Promise<any>;
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

    console.groupCollapsed(`｢objectiv:${this.transportName}｣ Initialized`);
    console.log(`Transports: ${args.map((transport) => transport.transportName).join(', ')}`);
    console.log(`First usable Transport: ${this.firstUsableTransport?.transportName ?? 'none'}`);
    console.groupEnd();
  }

  /**
   * Simply proxy the `handle` method to the usable TrackerTransport we found during construction, if any
   */
  async handle(...args: NonEmptyArray<TransportableEvent>): Promise<any> {
    if (!this.firstUsableTransport) {
      return Promise.reject(`${this.transportName}: no usable Transport found; make sure to verify usability first.`);
    }

    return this.firstUsableTransport.handle(...args);
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

    console.groupCollapsed(`｢objectiv:${this.transportName}｣ Initialized`);
    console.log(`Transports: ${args.map((transport) => transport.transportName).join(', ')}`);
    console.log(`Usable Transports: ${this.usableTransports.map((transport) => transport.transportName).join(', ')}`);
    console.groupEnd();
  }

  /**
   * Simply proxy the `handle` method to all the usable TrackerTransport instances we have.
   */
  async handle(...args: NonEmptyArray<TransportableEvent>): Promise<any> {
    if (!this.usableTransports.length) {
      return Promise.reject(`${this.transportName}: no usable Transports found; make sure to verify usability first.`);
    }

    return this.usableTransports.map((transport) => transport.handle(...args));
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

    console.groupCollapsed(`｢objectiv:${this.transportName}｣ Initialized`);
    console.log(`Transport: ${this.transport.transportName}`);
    console.log(`Queue: ${this.queue.queueName}`);
    console.groupEnd();

    if (this.isUsable()) {
      // Bind the handle function to its Transport instance to preserve its scope
      const processFunction = this.transport.handle.bind(this.transport);

      // Set the queue processFunction to transport.handle method: the queue will run Transport.handle for each batch
      this.queue.setProcessFunction(processFunction);

      // And start the Queue runner
      this.queue.startRunner();

      console.log(`%c｢objectiv:QueuedTransport｣ ${this.queue.queueName} runner started`, 'font-weight:bold');
    }
  }

  async handle(...args: NonEmptyArray<TransportableEvent>): Promise<any> {
    return Promise.all(args).then((events) => isNonEmptyArray(events) && this.queue.push(...events));
  }

  isUsable(): boolean {
    return this.transport.isUsable();
  }
}

/**
 * The configuration object of a RetryTransport. Requires a TrackerTransport instance.
 */
export type RetryTransportConfig = {
  /**
   * The TrackerTransport instance to wrap around. Retry Transport will invoke the wrapped TrackerTransport `handle`.
   */
  transport: TrackerTransport;

  /**
   * Optional. How many times we will retry before giving up. Defaults to 10;
   */
  maxAttempts?: number;

  /**
   * Optional. How much time we will keep retrying before giving up. Defaults to Infinity;
   */
  maxRetryMs?: number;

  /**
   * Optional. The following properties are used to calculate the exponential timeouts between attempts.
   *
   * Given an `attemptCount`, representing how many times we retried so far, this is the formula:
   *   min( round( minTimeoutMs * pow(retryFactor, attemptCount) ), maxTimeoutMs)
   */
  minTimeoutMs?: number; // defaults to 1000
  maxTimeoutMs?: number; // defaults to Infinity
  retryFactor?: number; // defaults to 2
};

/**
 * A RetryTransportAttempt is a TransportRetry worker.
 * TransportRetry creates a RetryTransportAttempt instance whenever its `handle` method is invoked.
 */
export class RetryTransportAttempt implements Required<RetryTransportConfig> {
  // RetryTransport State
  readonly transport: TrackerTransport;
  readonly maxAttempts: number;
  readonly maxRetryMs: number;
  readonly minTimeoutMs: number;
  readonly maxTimeoutMs: number;
  readonly retryFactor: number;

  /**
   * The list of Events to handle.
   */
  events: NonEmptyArray<TransportableEvent>;

  /**
   * A list of errors in reverse order. Eg: element 0 is the last error occurred. N-1 is the first.
   */
  errors: Error[];

  /**
   * How many times we have tried so far. Used in the calculation of the exponential backoff.
   */
  attemptCount: number;

  /**
   * Start time is persisted before each attempt and checked before retrying to verify if we exceeded maxRetryMs.
   */
  startTime: number;

  constructor(retryTransportInstance: RetryTransport, events: NonEmptyArray<TransportableEvent>) {
    this.transport = retryTransportInstance.transport;
    this.maxAttempts = retryTransportInstance.maxAttempts;
    this.maxRetryMs = retryTransportInstance.maxRetryMs;
    this.minTimeoutMs = retryTransportInstance.minTimeoutMs;
    this.maxTimeoutMs = retryTransportInstance.maxTimeoutMs;
    this.retryFactor = retryTransportInstance.retryFactor;
    this.events = events;
    this.errors = [];
    this.attemptCount = 1;
    this.startTime = Date.now();

    console.groupCollapsed(`｢objectiv:RetryTransportAttempt｣ Created`);
    console.log(`Transport: ${this.transport.transportName}`);
    console.log(`Max Attempts: ${this.maxAttempts}`);
    console.log(`Max Retry (ms): ${this.maxRetryMs}`);
    console.log(`Min Timeout (ms): ${this.minTimeoutMs}`);
    console.log(`Max Timeout (ms): ${this.maxTimeoutMs}`);
    console.log(`Retry Factor: ${this.retryFactor}`);
    console.group(`Events:`);
    console.log(this.events);
    console.groupEnd();
    console.groupEnd();
  }

  /**
   * Determines how much time we have to wait based on the number of attempts and the configuration variables
   */
  calculateNextTimeoutMs(attemptCount: number) {
    return Math.min(Math.round(this.minTimeoutMs * Math.pow(this.retryFactor, attemptCount)), this.maxTimeoutMs);
  }

  /**
   * Verifies if we exceeded maxAttempts or maxRetryMs before attempting to call the given Transport's `handle` method.
   * If promise rejections occur it invokes the `retry` method.
   */
  async run() {
    // Stop if we reached maxAttempts
    if (this.attemptCount > this.maxAttempts) {
      this.errors.unshift(new Error('maxAttempts reached'));
      return Promise.reject(this.errors);
    }

    // Stop if we reached maxRetryMs
    if (this.startTime && Date.now() - this.startTime >= this.maxRetryMs) {
      this.errors.unshift(new Error('maxRetryMs reached'));
      return Promise.reject(this.errors);
    }

    console.groupCollapsed(`｢objectiv:RetryTransportAttempt｣ Running`);
    console.log(`Attempt Count: ${this.attemptCount}`);
    console.log(`Events:`);
    console.log(this.events);
    console.groupEnd();

    // Attempt to transport the given Events. Catch any rejections and have `retry` handle them.
    return this.transport.handle(...this.events)
      .then((response) => {
        console.groupCollapsed(`｢objectiv:RetryTransportAttempt｣ Succeeded`);
        console.log(`Response:`);
        console.log(response);
        console.groupEnd();
        return response;
      })
      .catch((error) => {
      console.groupCollapsed(`｢objectiv:RetryTransportAttempt｣ Failed`);
      console.log(`Error:`);
      console.log(error);
      console.log(`Events:`);
      console.log(this.events);
      console.groupEnd();

      // Retry TransportSendErrors
      if (error instanceof TransportSendError) {
        return this.retry(error);
      }
      // And ignore any other errors
      return Promise.reject(error);
    });
  }

  /**
   * Handles the given error, waits for the appropriate time and `attempt`s again
   */
  async retry(error: Error): Promise<any> {
    // Push error in the list of errors
    this.errors.unshift(error);

    // Wait for the next timeout
    const nextTimeoutMs = this.calculateNextTimeoutMs(this.attemptCount);
    await new Promise((resolve) => setTimeout(resolve, nextTimeoutMs));

    // Increment number of attempts
    this.attemptCount++;

    console.groupCollapsed(`｢objectiv:RetryTransportAttempt｣ Retrying`);
    console.log(`Attempt Count: ${this.attemptCount}`);
    console.log(`Waited: ${nextTimeoutMs}`);
    console.log(`Error:`);
    console.log(error);
    console.log(`Events:`);
    console.log(this.events);
    console.groupEnd();

    // Run again
    return this.run();
  }
}

/**
 * A TrackerTransport implementing exponential backoff retries around a TrackerTransport handle method.
 * It allows to also specify maximum retry time and number of attempts.
 */
export class RetryTransport implements TrackerTransport {
  readonly transportName = 'RetryTransport';

  // RetryTransportConfig
  readonly transport: TrackerTransport;
  readonly maxAttempts: number;
  readonly maxRetryMs: number;
  readonly minTimeoutMs: number;
  readonly maxTimeoutMs: number;
  readonly retryFactor: number;

  // A list of attempts that are currently running
  attempts: RetryTransportAttempt[] = [];

  constructor(config: RetryTransportConfig) {
    this.transport = config.transport;

    /**
     * With these defaults the maximum execution time of an Attempt is ~ 17 minutes
     * 1000 + 2000 + 4000 + 8000 + 16000 + 32000 + 64000 + 128000 + 256000 + 512000 = 1023000 ms or 17.05 mins
     */
    this.maxAttempts = config.maxAttempts ?? 10;
    this.maxRetryMs = config.maxRetryMs ?? Infinity;
    this.minTimeoutMs = config.minTimeoutMs ?? 1000;
    this.maxTimeoutMs = config.maxTimeoutMs ?? Infinity;
    this.retryFactor = config.retryFactor ?? 2;

    if (this.minTimeoutMs <= 0) {
      throw new Error('minTimeoutMs must be at least 1');
    }

    if (this.minTimeoutMs > this.maxTimeoutMs) {
      throw new Error('minTimeoutMs cannot be bigger than maxTimeoutMs');
    }

    console.groupCollapsed(`｢objectiv:RetryTransport｣ Initialized`);
    console.log(`Transport: ${this.transport.transportName}`);
    console.log(`Max Attempts: ${this.maxAttempts}`);
    console.log(`Max Retry (ms): ${this.maxRetryMs}`);
    console.log(`Min Timeout (ms): ${this.minTimeoutMs}`);
    console.log(`Max Timeout (ms): ${this.maxTimeoutMs}`);
    console.log(`Retry Factor: ${this.retryFactor}`);
    console.groupEnd();
  }

  /**
   * Creates a RetryTransportAttempt for the given Events and runs it.
   */
  async handle(...args: NonEmptyArray<TransportableEvent>): Promise<any> {
    // Create a new RetryTransportAttempt instance to handle the given Events
    const attempt = new RetryTransportAttempt(this, args);

    // Push the new RetryTransportAttempt instance to state
    const attemptIndex = this.attempts.push(attempt);

    // Run attempt
    return attempt.run().finally(() => {
      // Regardless if the attempt was successful or not, clear up the `attempts` state when it's done.
      this.attempts.splice(attemptIndex - 1, 1);
    });
  }

  isUsable(): boolean {
    return this.transport.isUsable();
  }
}
