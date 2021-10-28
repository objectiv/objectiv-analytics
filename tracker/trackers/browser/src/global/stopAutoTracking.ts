import { trackerErrorHandler } from '../trackerErrorHandler';
import { AutoTrackingState } from './AutoTrackingState';

/**
 * Stops autoTracking
 */
export const stopAutoTracking = () => {
  try {
    // Nothing to do if we are not auto-tracking
    if (!AutoTrackingState.observerInstance) {
      return;
    }

    // Stop Mutation Observer
    AutoTrackingState.observerInstance.disconnect();
    AutoTrackingState.observerInstance = null;
  } catch (error) {
    trackerErrorHandler(error);
  }
};
