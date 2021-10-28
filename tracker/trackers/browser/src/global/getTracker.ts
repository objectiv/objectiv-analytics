import { BrowserTracker } from '../tracker/BrowserTracker';
import { getTrackerRepository } from './getTrackerRepository';

/**
 * Retrieves a specific instance of the tracker from the TrackerRepository.
 */
export const getTracker = (trackerId?: string): BrowserTracker => {
  const tracker = getTrackerRepository().get(trackerId);

  // Throw if we did not manage to get a tracker instance
  if (!tracker) {
    throw new Error('No Tracker found. Please create one via `makeTracker`.');
  }

  return tracker;
};
