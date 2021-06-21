import { makeURLChangedEvent } from '@objectiv/tracker-core';
import { ReactTracker } from './ReactTracker';
import { useTracker } from './TrackerContextProvider';
import { useTrackOnChange } from './useTrackOnChange';

/**
 * Triggers a URLChangedEvent whenever a different URL is detected via the Location API.
 * This hook is meant to be used in a component that always re-renders based on route changes. Eg: A React-router Route
 */
export const useTrackURLChanged = (tracker: ReactTracker = useTracker()) =>
  useTrackOnChange(location.href, makeURLChangedEvent(), tracker);
