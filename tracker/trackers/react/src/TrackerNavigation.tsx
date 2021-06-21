import { makeNavigationContext, Tracker } from '@objectiv/tracker-core';
import { ReactNode } from 'react';
import { ReactTracker } from './ReactTracker';
import { TrackerContextProvider, useTracker } from './TrackerContextProvider';
import { useTrackVisibility } from './useTrackVisibility';

/**
 * Tracker Navigation is a SectionProvider meant to wrap around menus, menu drawers and navigation elements in general.
 * The resulting provider will return a tracker extended with whatever contexts are already present in ancestor
 * TrackerContextProviders. Unless a tracker instance is provided to override this default behavior.
 *
 * Tracker Navigation tracks its own visibility automatically.
 *
 * TODO add better docs and some examples
 */
export const TrackerNavigation = ({
  id,
  children,
  tracker = useTracker(),
}: {
  id: string;
  children: ReactNode;
  tracker?: Tracker;
}) => {
  const navigationTracker = new ReactTracker(tracker, { location_stack: [makeNavigationContext({ id })] });
  useTrackVisibility(navigationTracker);

  return <TrackerContextProvider tracker={navigationTracker}>{children}</TrackerContextProvider>;
};
