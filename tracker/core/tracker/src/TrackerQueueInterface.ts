import { NonEmptyArray } from './helpers';
import { TrackerConsole } from './TrackerConsole';
import { TrackerEvent } from './TrackerEvent';
import { TrackerQueueStoreInterface } from './TrackerQueueStoreInterface';

/**
 * The definition of the runner function. Gets executed every batchDelayMs to process the Queue.
 */
export type TrackerQueueProcessFunction = (...args: NonEmptyArray<TrackerEvent>) => Promise<any>;

/**
 * Our Tracker Events Queue generic interface.
 */
export interface TrackerQueueInterface {
  /**
   * Optional. A TrackerConsole instance for logging.
   */
  readonly console?: TrackerConsole;

  /**
   * The TrackerQueueStore to use. Defaults to TrackerQueueMemoryStore
   */
  readonly store: TrackerQueueStoreInterface;

  /**
   * How many events to dequeue at the same time. Defaults to 10;
   */
  readonly batchSize: number;

  /**
   * How often to re-run and dequeue again, in ms. Defaults to 1000.
   */
  readonly batchDelayMs: number;

  /**
   * How many batches to process simultaneously. Defaults to 4.
   */
  readonly concurrency: number;

  /**
   * The function to execute every batchDelayMs. Must be set with `setProcessFunction` before calling `run`
   */
  processFunction?: TrackerQueueProcessFunction;

  /**
   * A name describing the Queue implementation for debugging purposes
   */
  readonly queueName: string;

  /**
   * Sets the processFunction to execute whenever run is called
   */
  setProcessFunction(processFunction: TrackerQueueProcessFunction): void;

  /**
   * Starts the runner process
   */
  startRunner(): void;

  /**
   * Adds one or more TrackerEvents to the Queue
   */
  push(...args: NonEmptyArray<TrackerEvent>): Promise<any>;

  /**
   * Adds one or more TrackerEvents to the Queue
   */
  readBatch(): Promise<TrackerEvent[]>;

  /**
   * Fetches a batch of Events from the Queue and executes the given `processFunction` with them.
   */
  run(): Promise<any>;

  /**
   * Empties the Queue
   */
  flush(): Promise<any>;

  /**
   * Returns whether all Events have been processed.
   */
  isIdle(): boolean;
}
