/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { isNonEmptyArray, NonEmptyArray } from './helpers';
import { TrackerEvent } from './TrackerEvent';
import { TrackerQueueInterface, TrackerQueueProcessFunction } from './TrackerQueueInterface';
import { TrackerQueueMemoryStore } from './TrackerQueueMemoryStore';
import { TrackerQueueStoreInterface } from './TrackerQueueStoreInterface';

/**
 * The configuration of a TrackerQueue
 */
export type TrackerQueueConfig = {
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
  readonly queueName = 'TrackerQueue';
  processFunction?: TrackerQueueProcessFunction;
  readonly store: TrackerQueueStoreInterface;
  readonly batchSize: number;
  readonly batchDelayMs: number;
  readonly concurrency: number;

  // Holds a list of Event IDs that are currently being processed
  processingEventIds: string[] = [];

  // Holds when we last sent a batch, used to determine if we should wait
  lastRunTimestamp: number = 0;

  // State to avoid concurrent runs
  running: boolean = false;

  /**
   * Initializes batching configuration with some sensible values.
   */
  constructor(config?: TrackerQueueConfig) {
    this.store = config?.store ?? new TrackerQueueMemoryStore();
    this.batchSize = config?.batchSize ?? 10;
    this.batchDelayMs = config?.batchDelayMs ?? 1000;
    this.concurrency = config?.concurrency ?? 4;

    if (globalThis.objectiv) {
      globalThis.objectiv.TrackerConsole.groupCollapsed(`｢objectiv:${this.queueName}｣ Initialized`);
      globalThis.objectiv.TrackerConsole.log(`Store: ${this.store.queueStoreName}`);
      globalThis.objectiv.TrackerConsole.log(`Batch Size: ${this.batchSize}`);
      globalThis.objectiv.TrackerConsole.log(`Batch Delay (ms): ${this.batchDelayMs}`);
      globalThis.objectiv.TrackerConsole.log(`Concurrency: ${this.concurrency}`);
      globalThis.objectiv.TrackerConsole.groupEnd();
    }
  }

  setProcessFunction(processFunction: TrackerQueueProcessFunction) {
    this.processFunction = processFunction;
  }

  async push(...args: NonEmptyArray<TrackerEvent>): Promise<any> {
    await this.store.write(...args);
    return this.run();
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

    if (this.running || this.isIdle()) {
      return false;
    }

    this.running = true;

    // Wait to avoid sending batches too close to each other, based on batchDelayMs
    const msSinceLastRun = Date.now() - this.lastRunTimestamp;
    if (msSinceLastRun < this.batchDelayMs) {
      await new Promise((resolve) => setTimeout(resolve, this.batchDelayMs - msSinceLastRun));
    }

    // Load and process as many Event batches as `concurrency` allows. For each Event we create a Promise.
    let processPromises: Promise<any>[] = [];

    for (let i = 0; i < this.concurrency; i++) {
      const eventsBatch = await this.readBatch();

      // No need to continue if there are no more Events to process
      if (!isNonEmptyArray(eventsBatch)) {
        break;
      }

      if (globalThis.objectiv) {
        globalThis.objectiv.TrackerConsole.groupCollapsed(`｢objectiv:${this.queueName}｣ Batch read`);
        globalThis.objectiv.TrackerConsole.log(`Events:`);
        globalThis.objectiv.TrackerConsole.log(eventsBatch);
        globalThis.objectiv.TrackerConsole.groupEnd();
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

    await Promise.all(processPromises);
    this.running = false;
    this.lastRunTimestamp = Date.now();
    return this.run();
  }

  async flush(): Promise<any> {
    return this.store.clear();
  }

  isIdle(): boolean {
    return this.store.length === 0 && this.processingEventIds.length === 0;
  }
}
