import { AbstractEvent } from '@objectiv/schema';
import { ReactTracker } from './ReactTracker';
import { useTracker } from './TrackerContextProvider';
import { useOnMount } from './useOnMount';

/**
 * A side effect that triggers the given TrackerEvent on mount.
 */
export const useTrackOnMount = (event: AbstractEvent, tracker: ReactTracker = useTracker()) => {
  useOnMount(() => {
    tracker.trackEvent(event);
  });
};
