import { AbstractEvent } from '@objectiv/schema';
import { ReactTracker } from './ReactTracker';
import { useTracker } from './TrackerContextProvider';
import { useOnUnmount } from './useOnUnmount';

/**
 * A side effect that triggers the given TrackerEvent on unmount.
 */
export const useTrackOnUnmount = (event: AbstractEvent, tracker: ReactTracker = useTracker()) => {
  useOnUnmount(() => {
    tracker.trackEvent(event);
  });
};
