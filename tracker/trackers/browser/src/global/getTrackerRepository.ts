import { TrackerRepository } from '@objectiv/tracker-core';
import { windowExists } from '../helpers';
import { BrowserTracker } from '../tracker/BrowserTracker';

/**
 * Retrieves the TrackerRepository instance from the window.objectiv global namespace
 */
export const getTrackerRepository = (): TrackerRepository<BrowserTracker> => {
  if (!windowExists()) {
    throw new Error('Cannot access the Window interface.');
  }

  return window.objectiv.trackers;
};
