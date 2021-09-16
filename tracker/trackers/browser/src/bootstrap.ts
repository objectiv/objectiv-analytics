import { windowExists } from './globals';
import { BrowserTracker } from './tracker/BrowserTracker';

/**
 * The interface of our namespace which will be extending the Window interface
 */

export interface ObjectivNamespace {
  tracker: BrowserTracker;
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
 * Initialized window global namespace, unless already existing
 */
if (windowExists()) {
  window.objectiv = window.objectiv || {
    tracker: null,
  };
}
