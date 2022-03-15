/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { AbstractLocationContext } from '@objectiv/schema';
import {
  generateUUID,
  getLocationPath,
  NoopConsoleImplementation,
  Tracker,
  TrackerConsole,
} from '@objectiv/tracker-core';
import { LocationContext } from '../types';

/**
 * LocationTree nodes have the same shape of LocationContext, but they can have a parent LocationNode themselves.
 */
export type LocationNode = LocationContext<AbstractLocationContext> & {
  /**
   * The parent LocationNode identifier.
   */
  parentLocationId: string | null;
};

/**
 * The Root LocationNode of LocationTree
 */
export const rootNode: LocationNode = {
  __location_context: true,
  __location_id: generateUUID(),
  _type: 'LocationTreeRoot',
  id: 'location-tree-root',
  parentLocationId: null,
};

/**
 * Internal state to hold a complete list of all known LocationNodes.
 * Each node, exception made for the root one, is a uniquely identifiable Location Context.
 * All nodes, except the root ine, have a parent LocationNode.
 */
export let locationNodes: LocationNode[] = [rootNode];

/**
 * Internal state to keep track of which identifiers are already known for a certain issue. This is used to prevent
 * notifying the developer of the same issues multiple times.
 *
 * NOTE: Currently we support only `collision` issues. As more checks are implemented this Map may change.
 */
export const errorCache = new Map<string, 'collision'>();

/**
 * LocationTree is a global object providing a few utility methods to interact with the `locationNodes` global state.
 * LocationContextWrapper makes sure to add new LocationNodes to the tree whenever a Location Wrapper is used.
 */
export const LocationTree = {
  /**
   * Completely resets LocationTree state. Mainly useful while testing.
   */
  clear: () => {
    locationNodes = [rootNode];
    errorCache.clear();
  },

  /**
   * Helper method to return a list of children of the given LocationNode
   */
  children: ({ __location_id }: LocationNode): LocationNode[] => {
    return locationNodes.filter(({ parentLocationId }) => parentLocationId === __location_id);
  },

  /**
   * Helper method to log and register an error for the given locationId
   *
   * NOTE: Currently we support only `collision` issues. As more checks are implemented the type parameter may change.
   */
  error: (locationId: string, message: string, type: 'collision' = 'collision') => {
    if (errorCache.get(locationId) !== type) {
      console.error(`｢objectiv｣ ${message}`);
      console.log(`Location Tree:`);
      LocationTree.log();
      errorCache.set(locationId, type);
    }
  },

  /**
   * Clears and re-initializes the LocationTree nodes based on the given Tracker's Plugins.
   *
   * This method receives an instance of the Tracker and infers LocationStack mutations from its Plugins.
   * All lifecycle methods of each Plugin are executed and LocationStack mutations, if any, are collected.
   * LocationContexts are then converted to LocationNodes and pushed in the LocationTree state.
   * The Root element of the LocationTree gets also adjusted accordingly, so that we may add more Nodes correctly.
   */
  initialize: (tracker: Tracker) => {
    LocationTree.clear();

    // Clone the given Tracker into a new one with only plugins configured
    const trackerClone = new Tracker({
      applicationId: tracker.applicationId,
      plugins: tracker.plugins,
    });

    // Disable Console while we replay `initialize` and `enrich` lifecycle methods
    const previousConsoleImplementation = TrackerConsole.implementation;
    TrackerConsole.setImplementation(NoopConsoleImplementation);

    // Replay plugins lifecycle methods
    trackerClone.plugins.initialize(trackerClone);
    trackerClone.plugins.enrich(trackerClone);

    // Restore console
    TrackerConsole.setImplementation(previousConsoleImplementation);

    // Convert AbstractLocationContext[] to LocationContext<AbstractLocationContext>[]
    const locationStack: LocationContext<AbstractLocationContext>[] = trackerClone.location_stack.map(
      (locationContext) => ({
        __location_id: generateUUID(),
        ...locationContext,
      })
    );

    // Add LocationStack Contexts to LocationTree and update what the root node should be
    locationStack.reduce(
      (
        parentLocationContext: LocationContext<AbstractLocationContext> | null,
        locationContext: LocationContext<AbstractLocationContext>
      ) => {
        LocationTree.add(locationContext, parentLocationContext);
        return locationContext;
      },
      null
    );
  },

  /**
   * Logs a readable version of the `locationNodes` state to the console
   */
  log: (locationNode?: LocationNode, depth = 0) => {
    let nodeToLog = locationNode;

    if (!nodeToLog) {
      nodeToLog = rootNode;
    } else {
      // Log the given node
      console.log('  '.repeat(depth) + nodeToLog._type + ':' + nodeToLog.id);

      // Increase depth
      depth++;
    }

    // Recursively log children, if any
    LocationTree.children(nodeToLog).forEach((childLocationNode: LocationNode) =>
      LocationTree.log(childLocationNode, depth)
    );
  },

  /**
   * Checks the validity of the `locationNodes` state.
   * Currently, we perform only Uniqueness Check: if identical branches are detected they will be logged to the console.
   *
   * Note: This method is invoked automatically when calling `LocationTree.add`.
   */
  validate: (
    locationNode?: LocationNode,
    locationStack: AbstractLocationContext[] = [],
    locationPaths: Set<string> = new Set()
  ) => {
    let nodeToValidate = locationNode;

    if (!nodeToValidate) {
      nodeToValidate = rootNode;
    } else {
      locationStack.push(nodeToValidate);

      // Collision detection
      const locationId = nodeToValidate.__location_id;
      const locationPath = getLocationPath(locationStack);
      const locationPathsSize = locationPaths.size;
      locationPaths.add(locationPath);

      if (locationPathsSize === locationPaths.size) {
        LocationTree.error(locationId, `Location collision detected: ${locationPath}`);
        // No point in continuing to validate this node children, exit early
        return;
      }
    }

    // Rerun validation for each child
    LocationTree.children(nodeToValidate).map((childLocationNode: LocationNode) => {
      LocationTree.validate(childLocationNode, [...locationStack], locationPaths);
    });
  },

  /**
   * Adds the given LocationContext to the `locationNodes` state, then invokes `LocationTree.validate` to report issues.
   *
   * Note: This method is invoked automatically by LocationContextWrapper.
   */
  add: (
    locationContext: LocationContext<AbstractLocationContext>,
    parentLocationContext: LocationContext<AbstractLocationContext> | null
  ) => {
    const parentLocationId = (parentLocationContext ?? rootNode).__location_id;

    // Create and push the new LocationNode into the LocationTree
    locationNodes.push({ ...locationContext, parentLocationId });

    // Run validation to check if the tree is still valid
    LocationTree.validate();
  },

  /**
   * Removes the LocationNode corresponding to the given LocationContext from the LocationTree and errorCache.
   * Performs also a recursive cleanup of orphaned nodes afterwards.
   *
   * Note: This method is invoked automatically by LocationContextWrapper.
   */
  remove: (locationContext: LocationContext<AbstractLocationContext>) => {
    locationNodes = locationNodes.filter(({ __location_id }) => __location_id !== locationContext.__location_id);
    errorCache.delete(locationContext.__location_id);

    const sizeBeforeCleanup = locationNodes.length;

    // Filter out all nodes that have a parentLocationId that does not exist anymore
    locationNodes = locationNodes.reduce((accumulator, locationNode) => {
      if (!locationNode.parentLocationId) {
        accumulator.push(locationNode);
      }
      if (locationNodes.some(({ __location_id }) => __location_id === locationNode.parentLocationId)) {
        accumulator.push(locationNode);
      }
      return accumulator;
    }, [] as LocationNode[]);

    // Keep running until the cleaned up tree stops changing in size
    if (sizeBeforeCleanup !== locationNodes.length) {
      LocationTree.remove(locationContext);
    }
  },
};