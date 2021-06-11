import { TrackerEvent } from './TrackerEvent';

/**
 * Our Tracker Events Queue generic interface.
 */
export interface TrackerQueue {
  /**
   * A name describing the Queue implementation for debugging purposes
   */
  readonly queueName: string;

  /**
   * How many events to dequeue at the same time
   */
  readonly batchSize: number;

  /**
   * How often to re-run and dequeue again
   */
  readonly batchDelayMs: number;

  /**
   * Adds one or more TrackerEvents to the Queue
   */
  enqueue(...args: [TrackerEvent, ...TrackerEvent[]]): void;

  /**
   * Retrieves the oldest available Item(s) from the Queue
   */
  dequeue(): TrackerEvent[];

  /**
   * Queue runner function. Simply executes the given `runFunction` with the dequeued events.
   */
  run(runFunction: (...args: TrackerEvent[]) => void): void;
}

/**
 * The configuration of a TrackerQueue
 */
export type TrackerQueueConfig = {
  /**
   * Optional. How many events to dequeue at the same time
   */
  readonly batchSize?: number;

  /**
   * Optional. How often to re-run and dequeue again
   */
  readonly batchDelayMs?: number;
};

/**
 * A very simple Memory Queue generic implementation based on a JavaScript array.
 * It uses setInterval for a continuously consuming runner.
 *
 * TODO Just a PoC. This is a way too simplistic approach. If the batch fails we just lost it. Need to add retry, etc
 *
 */
export class MemoryQueue implements TrackerQueue {
  readonly queueName = 'MemoryQueue';
  events: TrackerEvent[] = [];
  readonly batchSize: number;
  readonly batchDelayMs: number;

  /**
   * Initializes batching configuration with some sensible values.
   */
  constructor(config?: TrackerQueueConfig) {
    this.batchSize = config?.batchSize ?? 10;
    this.batchDelayMs = config?.batchDelayMs ?? 250;
  }

  enqueue(...args: [TrackerEvent, ...TrackerEvent[]]): void {
    this.events.push(...args);
  }

  dequeue(): TrackerEvent[] {
    return this.events.splice(0, this.batchSize);
  }

  run(runFunction: (...args: TrackerEvent[]) => void): void {
    setInterval(() => {
      const eventsBatch = this.dequeue();
      // No need to execute runFunction if the batch is empty
      if (eventsBatch.length) {
        runFunction(...eventsBatch);
      }
    }, this.batchDelayMs);
  }
}
