import { getTracker } from '../globals';
import { getLocationHref } from '../helpers';
import { TaggingAttribute } from '../TaggingAttribute';
import { BrowserTrackerConfig } from '../tracker/BrowserTracker';
import { trackApplicationLoaded, trackURLChange } from '../tracker/trackEventHelpers';
import { trackerErrorHandler } from '../trackerErrorHandler';
import { isTaggedElement } from '../typeGuards';
import { trackNewElements } from './trackNewElements';
import { trackRemovedElements } from './trackRemovedElements';
import { trackVisibilityHiddenEvent } from './trackVisibilityHiddenEvent';
import { trackVisibilityVisibleEvent } from './trackVisibilityVisibleEvent';

/**
 * Global state
 */
export const AutoTrackingState: {
  observerInstance: MutationObserver | null,
  applicationLoaded: boolean,
  previousURL: string | undefined,
} = {
  /**
   * Holds the instance to the Tagged Elements Mutation Observer created by `startAutoTracking`
   */
  observerInstance: null,

  /**
   * Whether we already tracked the ApplicationLoaded Event or not
   */
  applicationLoaded: false,

  /**
   * Holds the last seen URL
   */
  previousURL: getLocationHref(),
}

/**
 * The options that `startAutoTracking` accepts
 */
export type AutoTrackingOptions = Pick<BrowserTrackerConfig, 'trackURLChanges' | 'trackApplicationLoaded'>;

/**
 * Initializes our automatic tracking, based on Mutation Observer.
 * Also tracks application Loaded.
 * Safe to call multiple times: it will auto-track only once.
 */
export const startAutoTracking = (options?: AutoTrackingOptions) => {
  try {
    // Nothing to do if we are already auto-tracking
    if(AutoTrackingState.observerInstance) {
      return;
    }

    // Create Mutation Observer
    AutoTrackingState.observerInstance = new MutationObserver(makeMutationCallback(options?.trackURLChanges ?? true));

    // Start observing DOM
    AutoTrackingState.observerInstance.observe(document, {
      childList: true,
      subtree: true,
      attributes: true,
      attributeFilter: [TaggingAttribute.trackVisibility],
    });

    // Track ApplicationLoaded Event - once
    if ((options?.trackApplicationLoaded ?? true) && !AutoTrackingState.applicationLoaded) {
      AutoTrackingState.applicationLoaded = true;
      trackApplicationLoaded({ tracker: getTracker() });
    }
  } catch (error) {
    trackerErrorHandler(error);
  }
};

/**
 * Stops autoTracking
 */
export const stopAutoTracking = () => {
  try {
    // Nothing to do if we are not auto-tracking
    if(!AutoTrackingState.observerInstance) {
      return;
    }

    // Stop Mutation Observer
    AutoTrackingState.observerInstance.disconnect()
    AutoTrackingState.observerInstance = null;
  } catch (error) {
    trackerErrorHandler(error);
  }
};

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
