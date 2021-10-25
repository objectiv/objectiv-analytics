import { NonEmptyArray } from './helpers';
import { TrackerConsole } from './Tracker';
import { TrackerEvent } from './TrackerEvent';

/**
 * The TrackerQueueStoreConfig object.
 */
export type TrackerQueueStoreConfig = {
  /**
   * Optional. A TrackerConsole instance for logging.
   */
  console?: TrackerConsole;
};

/**
 * Our Tracker Queue Store generic interface.
 */
export interface TrackerQueueStoreInterface {
  /**
   * Optional. A TrackerConsole instance for logging.
   */
  readonly console?: TrackerConsole;

  /**
   * A name describing the Queue Store implementation for debugging purposes
   */
  readonly queueStoreName: string;

  /**
   * How many TrackerEvents are in the store
   */
  length: number;

  /**
   * Read Events from the store, if `size` is omitted all TrackerEvents will be returned
   */
  read(size?: number, filterPredicate?: (event: TrackerEvent) => boolean): Promise<TrackerEvent[]>;

  /**
   * Write Events to the store
   */
  write(...args: NonEmptyArray<TrackerEvent>): Promise<any>;

  /**
   * Delete TrackerEvents from the store by id
   */
  delete(TrackerEventIds: string[]): Promise<any>;

  /**
   * Delete all TrackerEvents from the store
   */
  clear(): Promise<any>;
}
