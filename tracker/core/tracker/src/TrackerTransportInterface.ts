import ExtendableError from 'es6-error';
import { NonEmptyArray } from './helpers';
import { TrackerConsole } from './TrackerConsole';
import { TrackerEvent } from './TrackerEvent';

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
 * The configuration of TrackerTransportTransportSwitch
 */
export type TrackerTransportConfig = {
  /**
   * Optional. A TrackerConsole instance for logging.
   */
  console?: TrackerConsole;
};

/**
 * The TrackerTransport interface provides a single function to handle one or more TrackerEvents.
 *
 * TrackerTransport implementations may vary depending on platform. Eg: web: fetch, node: https module, etc
 *
 * Also, simpler implementations can synchronously send TrackerEvents right away to the Collector while more complex
 * ones may leverage Queues, Workers and Storage for asynchronous sending, or batching.
 */
export interface TrackerTransportInterface {
  /**
   * Optional. A TrackerConsole instance for logging.
   */
  readonly console?: TrackerConsole;

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
