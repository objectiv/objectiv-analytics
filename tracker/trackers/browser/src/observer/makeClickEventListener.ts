import { BrowserTracker } from '../tracker/BrowserTracker';
import { trackClick } from '../tracker/trackEventHelpers';
import { TrackedElement } from '../typeGuards';
import isBubbledEvent from './isBubbledEvent';

/**
 * A factory to make the event listener to attach to new Tracked Elements with the `trackClicks` attributes set
 */
const makeClickEventListener = (element: TrackedElement, tracker: BrowserTracker) => {
  return (event: Event) => {
    /* istanbul ignore else - This is a difficult case to test and cover in Jest */
    if (!isBubbledEvent(element, event.target)) {
      trackClick({ element, tracker });
    }
  };
};

export default makeClickEventListener;
