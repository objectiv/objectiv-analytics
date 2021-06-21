import { makeItemContext, Tracker } from '@objectiv/tracker-core';
import { ReactNode } from 'react';
import { ReactTracker } from './ReactTracker';
import { TrackerContextProvider, useTracker } from './TrackerContextProvider';
import { useTrackVisibility } from './useTrackVisibility';

/**
 * Tracker Item is a SectionProvider meant to wrap around interactive elements that are not Buttons or Links. For
 * example Cards, Media Items, Content Items and so on.
 * The resulting provider will return a tracker extended with whatever contexts are already present in ancestor
 * TrackerContextProviders. Unless a tracker instance is provided to override this default behavior.
 *
 * Tracker Item tracks its own visibility automatically.
 *
 * TODO add better docs and some examples
 */
export const TrackerItem = ({
  id,
  children,
  tracker = useTracker(),
}: {
  id: string;
  children: ReactNode;
  tracker?: Tracker;
}) => {
  const itemTracker = new ReactTracker(tracker, { location_stack: [makeItemContext({ id })] });
  useTrackVisibility(itemTracker);

  return <TrackerContextProvider tracker={itemTracker}>{children}</TrackerContextProvider>;
};
