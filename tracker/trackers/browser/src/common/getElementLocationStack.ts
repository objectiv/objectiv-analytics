/*
 * Copyright 2021 Objectiv B.V.
 */

import { LocationStack } from '@objectiv/tracker-core';
import { BrowserTracker } from '../BrowserTracker';
import { TaggingAttribute } from '../definitions/TaggingAttribute';
import { TrackedElement } from '../definitions/TrackedElement';
import { findParentTaggedElements } from './findParentTaggedElements';
import { isTaggableElement } from './guards/isTaggableElement';
import { parseLocationContext } from './parsers/parseLocationContext';
import { trackerErrorHandler } from './trackerErrorHandler';

/**
 * Generates a location stack for the given Element. If a Tracker instance is provided, also predicts its mutations.
 *
 * 1. Traverses the DOM to reconstruct the component stack
 * 2. If a Tracker instance is provided, retrieves the Tracker's Location Stack
 * 3. Merges the two Location Stacks to reconstruct the full Location
 * 4. If a Tracker instance is provided, runs the Tracker's plugins `beforeTransport` lifecycle on the locationStack
 */
export const getElementLocationStack = (parameters: { element: TrackedElement; tracker?: BrowserTracker }) => {
  const locationStack: LocationStack = [];

  try {
    const { element, tracker } = parameters;

    // Add Tracker's location to the locationStack
    if (tracker) {
      locationStack.push(...tracker.location_stack);
    }

    // Traverse the DOM to reconstruct Element's Location
    if (isTaggableElement(element)) {
      // Retrieve Tagged Parent Elements
      const elementsStack = findParentTaggedElements(element).reverse();

      // Re-hydrate Location Stack
      elementsStack.forEach((element) => {
        // Get, parse, validate, hydrate and push Location Context in the Location Stack
        locationStack.push(parseLocationContext(element.getAttribute(TaggingAttribute.context)));
      });
    }

    // Add Plugins mutations to the locationStack - global_contexts are not a concern, so we pass an empty array
    if (tracker) {
      tracker.plugins.beforeTransport({ location_stack: locationStack, global_contexts: [] });
    }
  } catch (error) {
    trackerErrorHandler(error, parameters);
  }

  return locationStack;
};
