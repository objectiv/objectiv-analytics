import { makeApplicationLoadedEvent } from '@objectiv/tracker-core';
import { ReactTracker } from './ReactTracker';
import { useTracker } from './TrackerContextProvider';
import { useTrackOnMount } from './useTrackOnMount';

/**
 * Triggers an ApplicationLoadedEvent when the using component mounts for the first time.
 * This hook is meant to be used high up in the Application. Eg: right after initialization and before routing.
 */
export const useTrackApplicationLoaded = (tracker: ReactTracker = useTracker()) =>
  useTrackOnMount(makeApplicationLoadedEvent(), tracker);
