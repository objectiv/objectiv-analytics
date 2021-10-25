import {
  NonEmptyArray,
  TrackerConsole,
  TrackerEvent,
  TrackerQueueStoreConfig,
  TrackerQueueStoreInterface,
} from '@objectiv/tracker-core';

/**
 * The TrackerQueueLocalStorageStoreConfig object.
 */
export type TrackerQueueLocalStorageStoreConfig = TrackerQueueStoreConfig & {
  /**
   * Used to bind this queue to a specific tracker instance. This allows queues to persists across sessions.
   */
  trackerId: string;
};

/**
 * An Local Storage implementation of a TrackerQueueStore.
 */
export class TrackerQueueLocalStorageStore implements TrackerQueueStoreInterface {
  readonly console?: TrackerConsole;
  queueStoreName = `TrackerQueueLocalStorageStore`;
  readonly localStorageKey: string;

  constructor(config: TrackerQueueLocalStorageStoreConfig) {
    this.console = config.console;

    if (typeof localStorage === 'undefined') {
      throw new Error(`${this.queueStoreName}: failed to initialize: window.localStorage is not available.`);
    }

    this.localStorageKey = `objectiv-events-queue-${config.trackerId}`;

    if (this.console) {
      this.console.log(`%c｢objectiv:${this.queueStoreName}｣ Initialized`, 'font-weight: bold');
    }
  }

  getEventsFromLocalStorage(): TrackerEvent[] {
    try {
      return JSON.parse(localStorage.getItem(this.localStorageKey) ?? '[]');
    } catch (error) {
      if (this.console) {
        this.console.error(
          `%c｢objectiv:${this.queueStoreName}｣ Failed to parse Events from localStorage: ${error}`,
          'font-weight: bold'
        );
      }
    }
    return [];
  }

  writeEventsToLocalStorage(events: TrackerEvent[]) {
    try {
      localStorage.setItem(this.localStorageKey, JSON.stringify(events));
    } catch (error) {
      if (this.console) {
        this.console.error(
          `%c｢objectiv:${this.queueStoreName}｣ Failed to write Events to localStorage: ${error}`,
          'font-weight: bold'
        );
      }
    }
  }

  get length() {
    const events = this.getEventsFromLocalStorage();
    return events.length;
  }

  async read(size?: number, filterPredicate?: (event: TrackerEvent) => boolean): Promise<TrackerEvent[]> {
    let events = this.getEventsFromLocalStorage();
    if (filterPredicate) {
      events = events.filter(filterPredicate);
    }
    return events.slice(0, size);
  }

  async write(...args: NonEmptyArray<TrackerEvent>): Promise<any> {
    const events = this.getEventsFromLocalStorage();
    events.push(...args);
    this.writeEventsToLocalStorage(events);
  }

  async delete(trackerEventIds: string[]): Promise<any> {
    let events = this.getEventsFromLocalStorage();
    events = events.filter((trackerEvent) => !trackerEventIds.includes(trackerEvent.id));
    this.writeEventsToLocalStorage(events);
  }

  async clear(): Promise<any> {
    this.writeEventsToLocalStorage([]);
  }
}
