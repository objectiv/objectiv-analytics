import { BrowserTracker } from '../tracker/BrowserTracker';
import { trackClick } from '../tracker/trackEventHelpers';
import { TaggedElement } from '../typeGuards';
import { isBubbledEvent } from './isBubbledEvent';

/**
 * A factory to make the event listener to attach to new TaggedElements with the `trackClicks` attributes set
 */
export const makeClickEventListener = (element: TaggedElement, tracker: BrowserTracker) => {
  return (event: Event) => {
    /* istanbul ignore else - This is a difficult case to test and cover in Jest */
    if (!isBubbledEvent(element, event.target)) {
      trackClick({ element, tracker });
    }
  };
};
