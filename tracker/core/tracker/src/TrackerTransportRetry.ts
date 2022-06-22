/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { NonEmptyArray } from './helpers';
import { TrackerTransportInterface, TransportableEvent } from './TrackerTransportInterface';
import { TrackerTransportRetryAttempt } from './TrackerTransportRetryAttempt';

/**
 * The configuration object of a RetryTransport. Requires a TrackerTransport instance.
 */
export type TrackerTransportRetryConfig = {
  /**
   * The TrackerTransport instance to wrap around. Retry Transport will invoke the wrapped TrackerTransport `handle`.
   */
  transport: TrackerTransportInterface;

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
 * A TrackerTransport implementing exponential backoff retries around a TrackerTransport handle method.
 * It allows to also specify maximum retry time and number of attempts.
 */
export class TrackerTransportRetry implements TrackerTransportInterface {
  readonly transportName = 'TrackerTransportRetry';

  // RetryTransportConfig
  readonly transport: TrackerTransportInterface;
  readonly maxAttempts: number;
  readonly maxRetryMs: number;
  readonly minTimeoutMs: number;
  readonly maxTimeoutMs: number;
  readonly retryFactor: number;

  // A list of attempts that are currently running
  attempts: TrackerTransportRetryAttempt[] = [];

  constructor(config: TrackerTransportRetryConfig) {
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

    if (globalThis.objectiv.devTools) {
      globalThis.objectiv.devTools.TrackerConsole.groupCollapsed(`｢objectiv:${this.transportName}｣ Initialized`);
      globalThis.objectiv.devTools.TrackerConsole.log(`Transport: ${this.transport.transportName}`);
      globalThis.objectiv.devTools.TrackerConsole.log(`Max Attempts: ${this.maxAttempts}`);
      globalThis.objectiv.devTools.TrackerConsole.log(`Max Retry (ms): ${this.maxRetryMs}`);
      globalThis.objectiv.devTools.TrackerConsole.log(`Min Timeout (ms): ${this.minTimeoutMs}`);
      globalThis.objectiv.devTools.TrackerConsole.log(`Max Timeout (ms): ${this.maxTimeoutMs}`);
      globalThis.objectiv.devTools.TrackerConsole.log(`Retry Factor: ${this.retryFactor}`);
      globalThis.objectiv.devTools.TrackerConsole.groupEnd();
    }
  }

  /**
   * Creates a RetryTransportAttempt for the given Events and runs it.
   */
  async handle(...args: NonEmptyArray<TransportableEvent>): Promise<any> {
    // Create a new RetryTransportAttempt instance to handle the given Events
    const attempt = new TrackerTransportRetryAttempt(this, args);

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
