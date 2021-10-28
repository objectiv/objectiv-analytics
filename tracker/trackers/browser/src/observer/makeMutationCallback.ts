import { AutoTrackingState } from '../global/AutoTrackingState';
import { getTracker } from '../global/getTracker';
import { getLocationHref } from '../helpers';
import { trackURLChange } from '../tracker/trackEventHelpers';
import { trackerErrorHandler } from '../trackerErrorHandler';
import { isTaggedElement } from '../typeGuards';
import { trackNewElements } from './trackNewElements';
import { trackRemovedElements } from './trackRemovedElements';
import { trackVisibilityHiddenEvent } from './trackVisibilityHiddenEvent';
import { trackVisibilityVisibleEvent } from './trackVisibilityVisibleEvent';

/**
 * A factory to generate our mutation observer callback. It will observe:
 *
 * New DOM nodes added.
 * We use a Mutation Observer to monitor the DOM for subtrees being added.
 * When that happens we traverse the new Nodes and scout for Elements that have been enriched with our Tracking
 * Attributes. For those Elements we attach Event listeners which will automatically handle their tracking.
 *
 * Existing nodes changing.
 * The same Observer is also configured to monitor changes in our visibility attribute.
 * When we detect a change in the visibility of a tracked element we trigger the corresponding visibility events.
 *
 * Existing nodes being removed.
 * We also monitor nodes that are removed. If those nodes are Tracked Elements of which we were tracking visibility
 * we will trigger visibility: hidden events for them.
 *
 * SPA URL changes (default enabled, configurable)
 * We can leverage the same Observer to detect also URL changes. To do so we simply keep track of the last URL we have
 * detected previously and if it's different we automatically trigger a URL change event.
 *
 * Application Loaded Event (default enabled, configurable)
 * Triggered once
 */
export const makeMutationCallback = (trackURLChangeEvents: boolean): MutationCallback => {
  return (mutationsList) => {
    try {
      const tracker = getTracker();

      if (trackURLChangeEvents) {
        // Track SPA URL changes
        const currentURL = getLocationHref();
        if (currentURL !== AutoTrackingState.previousURL) {
          AutoTrackingState.previousURL = currentURL;
          trackURLChange({ tracker });
        }
      }

      // Track DOM changes
      mutationsList.forEach(({ addedNodes, removedNodes, target, attributeName }) => {
        // New DOM nodes mutation: attach event listeners to all Tracked Elements and track visibility:visible events
        addedNodes.forEach((addedNode) => {
          if (addedNode instanceof Element) {
            trackNewElements(addedNode, tracker);
          }
        });

        // Removed DOM nodes mutation: track visibility:hidden events
        removedNodes.forEach((removedNode) => {
          if (removedNode instanceof Element) {
            trackRemovedElements(removedNode, tracker);
          }
        });

        // Visibility attribute mutation (programmatic visibility change): determine and track visibility events
        if (attributeName && isTaggedElement(target)) {
          trackVisibilityVisibleEvent(target, tracker);
          trackVisibilityHiddenEvent(target, tracker);
        }
      });
    } catch (error) {
      trackerErrorHandler(error);
    }
  };
};
