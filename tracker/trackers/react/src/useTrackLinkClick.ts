import { LinkContext } from '@objectiv/schema';
import { trackLinkClick } from '@objectiv/tracker-web';
import { ReactTracker } from './ReactTracker';
import { useTracker } from './TrackerContextProvider';

/**
 * Event handler to be used for Link-like elements.
 */
export const useTrackLinkClick =
  (linkContext: LinkContext, tracker: ReactTracker = useTracker()) =>
  () =>
    trackLinkClick(linkContext, tracker);
