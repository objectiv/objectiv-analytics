import { Tracker } from './Tracker';
import { TrackerEvent } from './TrackerEvent';

/**
 * All possible lifecycle methods of a TrackerPlugin.
 */
export interface TrackerPluginLifecycleInterface {
  /**
   * Executed when the Tracker initializes.
   * Useful to register event listeners that execute autonomously. Eg: URLChangeEvent
   */
  initialize?: (tracker: Tracker) => void;

  /**
   * Executed before the TrackerEvent is handed over to the TrackerTransport.
   * Useful to gather Contexts that may have changed from the last TrackerEvent tracking. Eg: URL, Time, User, etc
   */
  beforeTransport?: (event: TrackerEvent) => void;
}
