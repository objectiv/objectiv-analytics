import { makeOverlayContext, Tracker } from '@objectiv/tracker-core';
import { ReactNode } from 'react';
import { ReactTracker } from './ReactTracker';
import { TrackerContextProvider, useTracker } from './TrackerContextProvider';
import { useTrackVisibility } from './useTrackVisibility';

/**
 * Tracker Overlay is a SectionProvider meant to wrap around popovers, tooltips, modals and layered content in general.
 * The resulting provider will return a tracker extended with whatever contexts are already present in ancestor
 * TrackerContextProviders. Unless a tracker instance is provided to override this default behavior.
 *
 * Tracker Overlay tracks its own visibility automatically.
 *
 * TODO add better docs and some examples
 */
export const TrackerOverlay = ({
  id,
  children,
  tracker = useTracker(),
}: {
  id: string;
  children: ReactNode;
  tracker?: Tracker;
}) => {
  const overlayTracker = new ReactTracker(tracker, { location_stack: [makeOverlayContext({ id })] });
  useTrackVisibility(overlayTracker);

  return <TrackerContextProvider tracker={overlayTracker}>{children}</TrackerContextProvider>;
};
