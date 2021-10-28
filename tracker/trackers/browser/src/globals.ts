import { TrackerRepository } from '@objectiv/tracker-core';
import { windowExists } from './helpers';
import { BrowserTracker } from './tracker/BrowserTracker';

/**
 * The interface of our namespace which will be extending the Window interface
 */
export interface ObjectivNamespace {
  trackers: TrackerRepository<BrowserTracker>;
}

/**
 * Window extension for our namespace
 */
declare global {
  interface Window {
    objectiv: ObjectivNamespace;
  }
}

/**
 * Initialize window global namespace, unless already existing
 */
if (windowExists()) {
  window.objectiv = window.objectiv || {
    trackers: new TrackerRepository(),
  };
}
