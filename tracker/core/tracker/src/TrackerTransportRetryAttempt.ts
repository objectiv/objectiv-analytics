/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { NonEmptyArray } from './helpers';
import { isTransportSendError, TrackerTransportInterface, TransportableEvent } from './TrackerTransportInterface';
import { TrackerTransportRetry, TrackerTransportRetryConfig } from './TrackerTransportRetry';

/**
 * The Interface of RetryTransportAttempts
 */
type TrackerTransportRetryAttemptInterface = Required<TrackerTransportRetryConfig>;

/**
 * A RetryTransportAttempt is a TransportRetry worker.
 * TransportRetry creates a RetryTransportAttempt instance whenever its `handle` method is invoked.
 */
export class TrackerTransportRetryAttempt implements TrackerTransportRetryAttemptInterface {
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

    if (globalThis.objectiv) {
      globalThis.objectiv.TrackerConsole.groupCollapsed(`｢objectiv:TrackerTransportRetryAttempt｣ Created`);
      globalThis.objectiv.TrackerConsole.log(`Transport: ${this.transport.transportName}`);
      globalThis.objectiv.TrackerConsole.log(`Max Attempts: ${this.maxAttempts}`);
      globalThis.objectiv.TrackerConsole.log(`Max Retry (ms): ${this.maxRetryMs}`);
      globalThis.objectiv.TrackerConsole.log(`Min Timeout (ms): ${this.minTimeoutMs}`);
      globalThis.objectiv.TrackerConsole.log(`Max Timeout (ms): ${this.maxTimeoutMs}`);
      globalThis.objectiv.TrackerConsole.log(`Retry Factor: ${this.retryFactor}`);
      globalThis.objectiv.TrackerConsole.group(`Events:`);
      globalThis.objectiv.TrackerConsole.log(this.events);
      globalThis.objectiv.TrackerConsole.groupEnd();
      globalThis.objectiv.TrackerConsole.groupEnd();
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

    if (globalThis.objectiv) {
      globalThis.objectiv.TrackerConsole.groupCollapsed(`｢objectiv:TrackerTransportRetryAttempt｣ Running`);
      globalThis.objectiv.TrackerConsole.log(`Attempt Count: ${this.attemptCount}`);
      globalThis.objectiv.TrackerConsole.log(`Events:`);
      globalThis.objectiv.TrackerConsole.log(this.events);
      globalThis.objectiv.TrackerConsole.groupEnd();
    }

    // Attempt to transport the given Events. Catch any rejections and have `retry` handle them.
    return this.transport
      .handle(...this.events)
      .then((response) => {
        if (globalThis.objectiv) {
          globalThis.objectiv.TrackerConsole.groupCollapsed(`｢objectiv:TrackerTransportRetryAttempt｣ Succeeded`);
          globalThis.objectiv.TrackerConsole.log(`Response:`);
          globalThis.objectiv.TrackerConsole.log(response);
          globalThis.objectiv.TrackerConsole.groupEnd();
        }

        return response;
      })
      .catch((error) => {
        if (globalThis.objectiv) {
          globalThis.objectiv.TrackerConsole.groupCollapsed(`｢objectiv:TrackerTransportRetryAttempt｣ Failed`);
          globalThis.objectiv.TrackerConsole.log(`Error:`);
          globalThis.objectiv.TrackerConsole.log(error);
          globalThis.objectiv.TrackerConsole.log(`Events:`);
          globalThis.objectiv.TrackerConsole.log(this.events);
          globalThis.objectiv.TrackerConsole.groupEnd();
        }

        // Retry TransportSendErrors
        if (isTransportSendError(error)) {
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

    if (globalThis.objectiv) {
      globalThis.objectiv.TrackerConsole.groupCollapsed(`｢objectiv:TrackerTransportRetryAttempt｣ Retrying`);
      globalThis.objectiv.TrackerConsole.log(`Attempt Count: ${this.attemptCount}`);
      globalThis.objectiv.TrackerConsole.log(`Waited: ${nextTimeoutMs}`);
      globalThis.objectiv.TrackerConsole.log(`Error:`);
      globalThis.objectiv.TrackerConsole.log(error);
      globalThis.objectiv.TrackerConsole.log(`Events:`);
      globalThis.objectiv.TrackerConsole.log(this.events);
      globalThis.objectiv.TrackerConsole.groupEnd();
    }

    // Run again
    return this.run();
  }
}
