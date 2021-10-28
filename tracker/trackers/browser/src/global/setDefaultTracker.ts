import { FlushQueueOptions, WaitForQueueOptions } from '../structs';
import { getTracker } from './getTracker';
import { getTrackerRepository } from './getTrackerRepository';

/**
 * Helper method to easily set a different default Tracker in the TrackerRepository.
 */
export const setDefaultTracker = async (
  parameters:
    | string
    | {
        trackerId: string;
        waitForQueue?: false | WaitForQueueOptions;
        flushQueue?: FlushQueueOptions;
      }
) => {
  let trackerId: string;
  let waitForQueue: undefined | WaitForQueueOptions;
  let flushQueue: undefined | FlushQueueOptions;

  // Some sensible defaults
  const defaultWaitForQueue = {}; // Wait for Queue with default options before switching default Tracker.
  const defaultFlushQueue = true; // Flush the Queue before switching default Tracker.

  if (typeof parameters === 'string') {
    trackerId = parameters;
    waitForQueue = defaultWaitForQueue;
    flushQueue = defaultFlushQueue;
  } else {
    trackerId = parameters.trackerId;
    waitForQueue = parameters.waitForQueue ?? defaultWaitForQueue;
    flushQueue = parameters.flushQueue ?? defaultFlushQueue;
  }

  // Get current default Tracker
  const tracker = getTracker();

  // Process waitForQueue
  let isQueueEmpty = true;
  if (waitForQueue) {
    isQueueEmpty = await tracker.waitForQueue(waitForQueue);
  }

  // Process flushQueue
  if (flushQueue === true || (flushQueue === 'onTimeout' && !isQueueEmpty)) {
    tracker.flushQueue();
  }

  // Set the new default Tracker
  getTrackerRepository().setDefault(trackerId);
};
