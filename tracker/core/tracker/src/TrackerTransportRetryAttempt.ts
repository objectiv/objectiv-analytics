import { NonEmptyArray } from './helpers';
import { TrackerConsole } from './Tracker';
import {
  TrackerTransportConfig,
  TrackerTransportInterface,
  TransportableEvent,
  TransportSendError,
} from './TrackerTransportInterface';
import { TrackerTransportRetry, TrackerTransportRetryConfig } from './TrackerTransportRetry';

/**
 * The Interface of RetryTransportAttempts
 */
type TrackerTransportRetryAttemptInterface = TrackerTransportConfig & Required<TrackerTransportRetryConfig>;

/**
 * A RetryTransportAttempt is a TransportRetry worker.
 * TransportRetry creates a RetryTransportAttempt instance whenever its `handle` method is invoked.
 */
export class TrackerTransportRetryAttempt implements TrackerTransportRetryAttemptInterface {
  readonly console?: TrackerConsole;

  // RetryTransport State
  readonly transport: TrackerTransportInterface;
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

  constructor(retryTransportInstance: TrackerTransportRetry, events: NonEmptyArray<TransportableEvent>) {
    this.console = retryTransportInstance.console;
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

    if (this.console) {
      this.console.groupCollapsed(`｢objectiv:TrackerTransportRetryAttempt｣ Created`);
      this.console.log(`Transport: ${this.transport.transportName}`);
      this.console.log(`Max Attempts: ${this.maxAttempts}`);
      this.console.log(`Max Retry (ms): ${this.maxRetryMs}`);
      this.console.log(`Min Timeout (ms): ${this.minTimeoutMs}`);
      this.console.log(`Max Timeout (ms): ${this.maxTimeoutMs}`);
      this.console.log(`Retry Factor: ${this.retryFactor}`);
      this.console.group(`Events:`);
      this.console.log(this.events);
      this.console.groupEnd();
      this.console.groupEnd();
    }
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

    if (this.console) {
      this.console.groupCollapsed(`｢objectiv:TrackerTransportRetryAttempt｣ Running`);
      this.console.log(`Attempt Count: ${this.attemptCount}`);
      this.console.log(`Events:`);
      this.console.log(this.events);
      this.console.groupEnd();
    }

    // Attempt to transport the given Events. Catch any rejections and have `retry` handle them.
    return this.transport
      .handle(...this.events)
      .then((response) => {
        if (this.console) {
          this.console.groupCollapsed(`｢objectiv:TrackerTransportRetryAttempt｣ Succeeded`);
          this.console.log(`Response:`);
          this.console.log(response);
          this.console.groupEnd();
        }

        return response;
      })
      .catch((error) => {
        if (this.console) {
          this.console.groupCollapsed(`｢objectiv:TrackerTransportRetryAttempt｣ Failed`);
          this.console.log(`Error:`);
          this.console.log(error);
          this.console.log(`Events:`);
          this.console.log(this.events);
          this.console.groupEnd();
        }

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

    if (this.console) {
      this.console.groupCollapsed(`｢objectiv:TrackerTransportRetryAttempt｣ Retrying`);
      this.console.log(`Attempt Count: ${this.attemptCount}`);
      this.console.log(`Waited: ${nextTimeoutMs}`);
      this.console.log(`Error:`);
      this.console.log(error);
      this.console.log(`Events:`);
      this.console.log(this.events);
      this.console.groupEnd();
    }

    // Run again
    return this.run();
  }
}
