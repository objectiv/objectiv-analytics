import { ButtonContext } from '@objectiv/schema';
import { trackButtonClick } from '@objectiv/tracker-web';
import { ReactTracker } from './ReactTracker';
import { useTracker } from './TrackerContextProvider';

/**
 * Event handler to be used for Button-like elements.
 */
export const useTrackButtonClick =
  (buttonContext: ButtonContext, tracker: ReactTracker = useTracker()) =>
  () =>
    trackButtonClick(buttonContext, tracker);
