/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { NonEmptyArray } from './helpers';
import { TrackerEvent } from './TrackerEvent';
import { TrackerQueueStoreInterface } from './TrackerQueueStoreInterface';

/**
 * An in-memory implementation of a TrackerQueueStore.
 *
 * TODO: move this to its own package: MemoryQueueStore
 */
export class TrackerQueueMemoryStore implements TrackerQueueStoreInterface {
  queueStoreName = `TrackerQueueMemoryStore`;
  events: TrackerEvent[] = [];

  constructor() {
    globalThis.objectiv.devTools?.TrackerConsole.log(
      `%c｢objectiv:${this.queueStoreName}｣ Initialized`,
      'font-weight: bold'
    );
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
  }

  async delete(trackerEventIds: string[]): Promise<any> {
    this.events = this.events.filter((trackerEvent) => !trackerEventIds.includes(trackerEvent.id));
  }

  async clear(): Promise<any> {
    this.events = [];
  }

  get length(): number {
    return this.events.length;
  }
}
