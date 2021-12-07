/*
 * Copyright 2021 Objectiv B.V.
 */

import { TrackerConsole, TrackerElementLocations } from '@objectiv/tracker-core';
import { getLocationHref } from '../common/getLocationHref';
import { isTaggedElement } from '../common/guards/isTaggedElement';
import { trackerErrorHandler } from '../common/trackerErrorHandler';
import { TaggingAttribute } from '../definitions/TaggingAttribute';
import { trackURLChange } from '../eventTrackers/trackURLChange';
import { getTracker } from '../getTracker';
import { AutoTrackingState } from './AutoTrackingState';
import { trackNewElements } from './trackNewElements';
import { trackRemovedElements } from './trackRemovedElements';
import { trackVisibilityHiddenEvent } from './trackVisibilityHiddenEvent';
import { trackVisibilityVisibleEvent } from './trackVisibilityVisibleEvent';

/**
 * A factory to generate our mutation observer callback. It will observe:
 *
 * New DOM nodes added.
 * We use a Mutation Observer to monitor the DOM for subtrees being added.
 * When that happens we traverse the new Nodes and scout for Elements that have been enriched with our Tagging
 * Attributes. For those Elements we attach Event listeners which will automatically handle their tracking.
 * New Elements are also added to TrackerElementLocations and their Location Stack is validated for uniqueness.
 *
 * Existing nodes changing.
 * The same Observer is also configured to monitor changes in our visibility and element id attributes.
 * When we detect a change in the visibility of a tagged element we trigger the corresponding visibility events.
 * Element id changes are used to keep the TrackerElementLocations in sync with the DOM.
 *
 * Existing nodes being removed.
 * We also monitor nodes that are removed. If those nodes are Tagged Elements of which we were tracking visibility
 * we will trigger visibility: hidden events for them.
 * We also clean them up from TrackerElementLocations.
 *
 * SPA URL changes (default enabled, configurable)
 * We can leverage the same Observer to detect also URL changes. To do so we simply keep track of the last URL we have
 * detected previously and if it's different we automatically trigger a URL change event.
 */
export const makeMutationCallback = (trackURLChangeEvents: boolean, console?: TrackerConsole): MutationCallback => {
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
      mutationsList.forEach(({ addedNodes, removedNodes, target, attributeName, oldValue }) => {
        // Element ID change for programmatically instrumented elements - keep TrackerState in sync
        if (attributeName === TaggingAttribute.elementId && oldValue) {
          TrackerElementLocations.delete(oldValue);
        }

        // New DOM nodes mutation: attach event listeners to all Tagged Elements and track visibility:visible events
        addedNodes.forEach((addedNode) => {
          if (addedNode instanceof Element) {
            trackNewElements(addedNode, tracker, console);
          }
        });

        // Removed DOM nodes mutation: track visibility:hidden events
        removedNodes.forEach((removedNode) => {
          if (removedNode instanceof Element) {
            trackRemovedElements(removedNode, tracker);
          }
        });

        // Visibility attribute mutation (programmatic visibility change): determine and track visibility events
        if (attributeName === TaggingAttribute.trackVisibility && isTaggedElement(target)) {
          trackVisibilityVisibleEvent(target, tracker);
          trackVisibilityHiddenEvent(target, tracker);
        }
      });
    } catch (error) {
      trackerErrorHandler(error);
    }
  };
};
