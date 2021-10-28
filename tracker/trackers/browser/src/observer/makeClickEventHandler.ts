import { TrackClicksOptions } from '../structs';
import { TaggingAttribute } from '../TaggingAttribute';
import { BrowserTracker } from '../tracker/BrowserTracker';
import { trackClick } from '../tracker/trackEventHelpers';
import { isTaggedElement, TaggedElement } from '../typeGuards';

/**
 * A factory to make the event handler to attach to new TaggedElements with the `trackClicks` attributes set
 */
export const makeClickEventHandler = (
  element: TaggedElement,
  tracker: BrowserTracker,
  trackClicksOptions?: TrackClicksOptions
) => {
  return async function clickEventHandler(event: Event) {
    if (
      // Either the Event's target is the TaggedElement itself
      event.target === element ||
      // Or the Event's currentTarget is am Element tagged to track Clicks (eg: the Event bubbled up to from a child)
      (isTaggedElement(event.currentTarget) && event.currentTarget.hasAttribute(TaggingAttribute.trackClicks))
    ) {
      trackClick({ element, tracker });

      // If required prevent this event from propagating and attempt to wait for it to be fully executed
      if (trackClicksOptions) {
        const { waitForQueue, flushQueue } = trackClicksOptions;

        // Clone the original Event before altering it - `as any` needed due to TS constructors being just `Function`s
        const eventClone = new (event.constructor as any)(event.type, event);

        // Prevent this event from being processed by the user agent and to stop propagating to any other handler
        event.preventDefault();
        event.stopImmediatePropagation();

        let isQueueEmpty = true;
        if (waitForQueue) {
          // Attempt to wait for the Tracker to finish up its work - this is best-effort: may or may not timeout
          isQueueEmpty = await tracker.waitForQueue(waitForQueue);
        }

        // Flush the Queue - unless waitUntilTrackedOptions has been specifically set not to do so
        if (flushQueue === true || (flushQueue === 'onTimeout' && !isQueueEmpty)) {
          tracker.flushQueue();
        }

        // Remove our event handler. This allows us to dispatch the original Event without our handler interfering
        element.removeEventListener(event.type, clickEventHandler, true);

        // Dispatch the original Event via its clone - since our event handler is gone it will dispatch normally
        element.dispatchEvent(eventClone);

        // Re-attach a new event handler to the original element
        element.addEventListener(event.type, makeClickEventHandler(element, tracker, trackClicksOptions), true);
      }
    }
  };
};
