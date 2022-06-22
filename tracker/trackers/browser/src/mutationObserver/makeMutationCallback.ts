/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { isTaggedElement } from '../common/guards/isTaggedElement';
import { parseLocationContext } from '../common/parsers/parseLocationContext';
import { trackerErrorHandler } from '../common/trackerErrorHandler';
import { TaggingAttribute } from '../definitions/TaggingAttribute';
import { getTracker } from '../getTracker';
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
 */
export const makeMutationCallback = (): MutationCallback => {
  return (mutationsList) => {
    try {
      const tracker = getTracker();

      // Track DOM changes
      mutationsList.forEach(({ addedNodes, removedNodes, target, attributeName, oldValue }) => {
        // Element ID change for programmatically instrumented elements - keep TrackerState in sync
        if (globalThis.objectiv.devTools && attributeName === TaggingAttribute.elementId && oldValue) {
          const element = document.querySelector(`[${TaggingAttribute.elementId}='${oldValue}']`);
          if (element) {
            globalThis.objectiv.devTools.LocationTree.remove(
              parseLocationContext(element.getAttribute(TaggingAttribute.context))
            );
          }
        }

        // New DOM nodes mutation: attach event listeners to all Tagged Elements and track visibility:visible events
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
