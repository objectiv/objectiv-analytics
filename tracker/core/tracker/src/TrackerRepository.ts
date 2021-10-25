import { Tracker } from './Tracker';
import { TrackerRepositoryInterface } from './TrackerRepositoryInterface';

/**
 * TrackerRepository allows developers to create and use multiple Tracker instances in the same Application.
 */
export class TrackerRepository<T extends Tracker> implements TrackerRepositoryInterface<T> {
  trackersMap = new Map<string, T>();
  defaultTracker?: T;

  add(newInstance: T) {
    if (this.trackersMap.has(newInstance.trackerId)) {
      console.error(`｢objectiv:TrackerRepository｣ Tracker \`${newInstance.trackerId}\` already exists.`);
      return;
    }
    this.trackersMap.set(newInstance.trackerId, newInstance);
    if (!this.defaultTracker) {
      this.defaultTracker = newInstance;
    }
  }

  delete(trackerId: string) {
    if (this.defaultTracker && this.defaultTracker.trackerId === trackerId) {
      if (this.trackersMap.size > 1) {
        console.error(
          `｢objectiv:TrackerRepository｣ \`${trackerId}\` is the default Tracker. Please set another as default before deleting it.`
        );
        return;
      }

      this.defaultTracker = undefined;
    }

    this.trackersMap.delete(trackerId);
  }

  get(trackerId?: string) {
    if (this.trackersMap.size === 0) {
      console.error(`｢objectiv:TrackerRepository｣ There are no Trackers.`);
      return;
    }

    if (trackerId) {
      const trackerInstance = this.trackersMap.get(trackerId);

      if (!trackerInstance) {
        console.error(`｢objectiv:TrackerRepository｣ Tracker \`${trackerId}\` not found.`);
        return;
      }

      return this.trackersMap.get(trackerId);
    }

    return this.defaultTracker;
  }

  setDefault(trackerId: string) {
    if (!this.trackersMap.has(trackerId)) {
      console.error(`｢objectiv:TrackerRepository｣ Tracker \`${trackerId}\` not found.`);
      return;
    }

    this.defaultTracker = this.trackersMap.get(trackerId);
  }

  activateAll() {
    this.trackersMap.forEach((tracker) => tracker.setActive(true));
  }

  deactivateAll() {
    this.trackersMap.forEach((tracker) => tracker.setActive(false));
  }

  flushAllQueues() {
    this.trackersMap.forEach((tracker) => tracker.flushQueue());
  }
}
