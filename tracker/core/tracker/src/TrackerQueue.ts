import { isNonEmptyArray, NonEmptyArray } from './helpers';
import { TrackerConsole } from './Tracker';
import { TrackerEvent } from './TrackerEvent';
import { TrackerQueueInterface, TrackerQueueProcessFunction } from './TrackerQueueInterface';
import { TrackerQueueMemoryStore } from './TrackerQueueMemoryStore';
import { TrackerQueueStoreInterface } from './TrackerQueueStoreInterface';

/**
 * The configuration of a TrackerQueue
 */
export type TrackerQueueConfig = {
  /**
   * Optional. A TrackerConsole instance for logging.
   */
  console?: TrackerConsole;

  /**
   * Optional. The TrackerQueueStore to use. Defaults to TrackerQueueMemoryStore
   */
  store?: TrackerQueueStoreInterface;

  /**
   * Optional. How many events to dequeue at the same time. Defaults to 10;
   */
  batchSize?: number;

  /**
   * Optional. How often to re-run and dequeue again, in ms. Defaults to 1000.
   */
  batchDelayMs?: number;

  /**
   * Optional. How many batches to process simultaneously. Defaults to 4.
   */
  concurrency?: number;
};

/**
 * A very simple Batched Queue implementation.
 */
export class TrackerQueue implements TrackerQueueInterface {
  readonly console?: TrackerConsole;
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
    this.console = config?.console;
    this.store = config?.store ?? new TrackerQueueMemoryStore({ console: config?.console });
    this.batchSize = config?.batchSize ?? 10;
    this.batchDelayMs = config?.batchDelayMs ?? 1000;
    this.concurrency = config?.concurrency ?? 4;

    if (this.console) {
      this.console.groupCollapsed(`｢objectiv:${this.queueName}｣ Initialized`);
      this.console.log(`Store: ${this.store.queueStoreName}`);
      this.console.log(`Batch Size: ${this.batchSize}`);
      this.console.log(`Batch Delay (ms): ${this.batchDelayMs}`);
      this.console.log(`Concurrency: ${this.concurrency}`);
      this.console.groupEnd();
    }
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

      if (this.console) {
        this.console.groupCollapsed(`｢objectiv:${this.queueName}｣ Batch read`);
        this.console.log(`Events:`);
        this.console.log(eventsBatch);
        this.console.groupEnd();
      }

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

  async flush(): Promise<any> {
    return this.store.clear();
  }

  isIdle(): boolean {
    return this.store.length === 0 && this.processingEventIds.length === 0;
  }
}
