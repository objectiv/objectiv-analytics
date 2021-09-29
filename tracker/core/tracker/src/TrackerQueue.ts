import { isNonEmptyArray, NonEmptyArray } from './helpers';
import { TrackerEvent } from './TrackerEvent';

/**
 * Our Tracker Queue Store generic interface.
 */
export interface TrackerQueueStoreInterface {
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
   * Delete TrackerEvents from the store
   */
  delete(TrackerEventIds: string[]): Promise<any>;
}

/**
 * An in-memory implementation of a TrackerQueueStore.
 */
export class TrackerQueueMemoryStore implements TrackerQueueStoreInterface {
  queueStoreName = `TrackerQueueMemoryStore`;
  length: number = 0;
  events: TrackerEvent[] = [];

  constructor() {
    console.log(`%c｢objectiv:${this.queueStoreName}｣ Initialized`, 'font-weight: bold');
  }

  async read(size?: number, filterPredicate?: (event: TrackerEvent) => boolean): Promise<TrackerEvent[]> {
    let events = this.events;
    if (filterPredicate) {
      events = events.filter(filterPredicate);
    }
    return events.slice(0, size);
  }

  async write(...args: NonEmptyArray<TrackerEvent>): Promise<any> {
    this.events.push(...args);
    this.updateLength();
  }

  async delete(trackerEventIds: string[]): Promise<any> {
    this.events = this.events.filter((trackerEvent) => !trackerEventIds.includes(trackerEvent.id));
    this.updateLength();
  }

  updateLength(): void {
    this.length = this.events.length;
  }
}

/**
 * The definition of the runner function. Gets executed every batchDelayMs to process the Queue.
 */
type TrackerQueueProcessFunction = (...args: NonEmptyArray<TrackerEvent>) => Promise<any>;

/**
 * The configuration of a TrackerQueue
 */
export type TrackerQueueConfig = {
  /**
   * Optional. The TrackerQueueStore to use. Defaults to TrackerQueueMemoryStore
   */
  readonly store?: TrackerQueueStoreInterface;

  /**
   * Optional. How many events to dequeue at the same time. Defaults to 10;
   */
  readonly batchSize?: number;

  /**
   * Optional. How often to re-run and dequeue again, in ms. Defaults to 1000.
   */
  readonly batchDelayMs?: number;

  /**
   * Optional. How many batches to process simultaneously. Defaults to 4.
   */
  readonly concurrency?: number;
};

/**
 * Our Tracker Events Queue generic interface.
 */
export interface TrackerQueueInterface extends Required<TrackerQueueConfig> {
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
}

/**
 * A very simple Batched Queue implementation.
 */
export class TrackerQueue implements TrackerQueueInterface {
  readonly queueName = 'TrackerQueue';
  processFunction?: TrackerQueueProcessFunction;
  readonly store: TrackerQueueStoreInterface;
  readonly batchSize: number;
  readonly batchDelayMs: number;
  readonly concurrency: number;

  // FIXME make this an array of arrays, so we may know how many batches are in there as well
  // Hold a list of Event IDs that are currently being processed
  processingEventIds: string[] = [];

  /**
   * Initializes batching configuration with some sensible values.
   */
  constructor(config?: TrackerQueueConfig) {
    this.store = config?.store ?? new TrackerQueueMemoryStore();
    this.batchSize = config?.batchSize ?? 10;
    this.batchDelayMs = config?.batchDelayMs ?? 1000;
    this.concurrency = config?.concurrency ?? 4;

    console.groupCollapsed(`｢objectiv:${this.queueName}｣ initialized`);
    console.log(`Store: ${this.store.queueStoreName}`);
    console.log(`Batch Size: ${this.batchSize}`);
    console.log(`Batch Delay (ms): ${this.batchDelayMs}`);
    console.log(`Concurrency: ${this.concurrency}`);
    console.groupEnd();
  }

  setProcessFunction(processFunction: TrackerQueueProcessFunction) {
    this.processFunction = processFunction;
  }

  startRunner() {
    setInterval(async () => {
      await this.run();
    }, this.batchDelayMs);
  }

  async push(...args: NonEmptyArray<TrackerEvent>): Promise<any> {
    return this.store.write(...args);
  }

  async readBatch(): Promise<TrackerEvent[]> {
    const eventsBatch = await this.store.read(this.batchSize, (event) => !this.processingEventIds.includes(event.id));

    // Push Event Ids in the processing list, so the next readBatch will not pick these up
    this.processingEventIds.push(...eventsBatch.map((event) => event.id));

    return eventsBatch;
  }

  async run(): Promise<any> {
    if (!this.processFunction) {
      return Promise.reject('TrackerQueue `processFunction` has not been set.');
    }

    // Load and process as many Event batches as `concurrency` allows. For each Event we create a Promise.
    let processPromises: Promise<any>[] = [];

    for (let i = 0; i < this.concurrency; i++) {
      const eventsBatch = await this.readBatch();

      // No need to continue if there are no more Events to process
      if (!isNonEmptyArray(eventsBatch)) {
        return;
      }

      console.groupCollapsed(`｢objectiv:${this.queueName}｣ Batch read`);
      console.log(`Events:`);
      console.log(eventsBatch);
      console.groupEnd();

      // Gather Event Ids. Used for both deletion and processingEventIds cleanup.
      const eventsBatchIds = eventsBatch.map((event) => event.id);

      // Queue process function
      processPromises.push(
        this.processFunction(...eventsBatch)
          // Delete Events from Store when the process function promise resolves
          .then(() => {
            this.store.delete(eventsBatchIds);
          })
          // Delete Event Ids from processing list, regardless if the processing was successful or not
          .finally(() => {
            this.processingEventIds = this.processingEventIds.filter((eventId) => !eventsBatchIds.includes(eventId));
          })
      );
    }

    return Promise.all(processPromises);
  }
}
