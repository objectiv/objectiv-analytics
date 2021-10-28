import { startAutoTracking } from '../global/startAutoTracking';
import { BrowserTracker, BrowserTrackerConfig } from '../tracker/BrowserTracker';
import { getTrackerRepository } from './getTrackerRepository';

/**
 * Allows to easily create and configure a new BrowserTracker instance and also starts auto tracking
 */
export const makeTracker = (trackerConfig: BrowserTrackerConfig): BrowserTracker => {
  const newTracker = new BrowserTracker(trackerConfig);
  const trackerRepository = getTrackerRepository();

  trackerRepository.add(newTracker);
  startAutoTracking(trackerConfig);

  return newTracker;
};
