/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { Tracker, WaitForQueueParameters } from './Tracker';

/**
 * The generic interface of the TrackerRepository
 */
export interface TrackerRepositoryInterface<T extends Tracker> {
  /**
   * A Map of all Tracker instances by `trackerId`
   */
  trackersMap: Map<string, T>;

  /**
   * The default Tracker instance that will be returned when invoking `getTracker` without `trackerId` parameter
   */
  defaultTracker?: T;

  /**
   * Adds a new Tracker instance to the trackersMap
   */
  add(newInstance: T): void;

  /**
   * Deletes Tracker instance from the trackersMap by `trackerId`
   */
  delete(trackerId: string): void;

  /**
   * Get a Tracker instance from the trackersMap by `trackerId`
   */
  get(trackerId?: string): T | undefined;

  /**
   * Changes the default Tracker instance by specifying a `trackerId`
   */
  setDefault(trackerId: string): void;

  /**
   * Sets all Tracker instances as active
   */
  activateAll(): void;

  /**
   * Sets all Tracker instances as inactive
   */
  deactivateAll(): void;

  /**
   * Flushes all Tracker instances Queues
   */
  flushAllQueues(): void;

  /**
   * Waits for the queues of all Trackers to be idle, or flushed
   */
  waitForAllQueues(parameters?: WaitForQueueParameters): Promise<true>;
}
