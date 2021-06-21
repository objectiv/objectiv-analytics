import { makeSectionContext, Tracker } from '@objectiv/tracker-core';
import { ReactNode } from 'react';
import { ReactTracker } from './ReactTracker';
import { TrackerContextProvider, useTracker } from './TrackerContextProvider';
import { useTrackVisibility } from './useTrackVisibility';

/**
 * Tracker Section wraps a logical section under a new TrackerContextProvider.
 * The resulting provider will return a tracker extended with whatever contexts are already present in ancestor
 * TrackerContextProviders. Unless a tracker instance is provided to override this default behavior.
 *
 * Tracker Section tracks its own visibility automatically.
 *
 * TODO add better docs and some examples
 */
export const TrackerSection = ({
  id,
  children,
  tracker = useTracker(),
}: {
  id: string;
  children: ReactNode;
  tracker?: Tracker;
}) => {
  const sectionTracker = new ReactTracker(tracker, { location_stack: [makeSectionContext({ id })] });
  useTrackVisibility(sectionTracker);

  return <TrackerContextProvider tracker={sectionTracker}>{children}</TrackerContextProvider>;
};
