/*
 * Copyright 2022 Objectiv B.V.
 */

import { AbstractLocationContext } from '@objectiv/schema';
import { generateGUID, LocationNode, LocationTreeInterface } from '@objectiv/tracker-core';
import { EventRecorder } from './EventRecorder';
import { getLocationPath } from './getLocationPath';
import { TrackerConsole } from './TrackerConsole';

/**
 * The Root LocationNode of LocationTree
 */
export const rootNode: LocationNode = {
  __location_context: true,
  __instance_id: generateGUID(),
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
export const LocationTree: LocationTreeInterface = {
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
  children: ({ __instance_id }: LocationNode): LocationNode[] => {
    return locationNodes.filter(({ parentLocationId }) => parentLocationId === __instance_id);
  },

  /**
   * Helper method to log and register an error for the given locationId
   *
   * NOTE: Currently we support only `collision` issues. As more checks are implemented the type parameter may change.
   */
  error: (locationId: string, message: string, type: 'collision' = 'collision') => {
    if (errorCache.get(locationId) !== type) {
      const errorMessage = `｢objectiv｣ ${message}`;

      EventRecorder.error(errorMessage);

      TrackerConsole.error(`｢objectiv｣ ${message}`);
      TrackerConsole.log(`Location Tree:`);
      LocationTree.log();
      errorCache.set(locationId, type);
    }
  },

  /**
   * Logs a readable version of the `locationNodes` state to the TrackerConsole
   */
  log: (locationNode?: LocationNode, depth = 0) => {
    let nodeToLog = locationNode;

    if (!nodeToLog) {
      nodeToLog = rootNode;
    } else {
      // Log the given node
      TrackerConsole.log('  '.repeat(depth) + nodeToLog._type + ':' + nodeToLog.id);

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
   * Currently, we perform only Collision Checks: if identical branches are detected they get logged to TrackerConsole.
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
      const locationId = nodeToValidate.__instance_id;
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
  add: (locationContext: AbstractLocationContext, parentLocationContext: AbstractLocationContext | null) => {
    const parentLocationId = (parentLocationContext ?? rootNode).__instance_id;

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
  remove: (locationContext: AbstractLocationContext) => {
    locationNodes = locationNodes.filter(({ __instance_id }) => __instance_id !== locationContext.__instance_id);
    errorCache.delete(locationContext.__instance_id);

    const sizeBeforeCleanup = locationNodes.length;

    // Filter out all nodes that have a parentLocationId that does not exist anymore
    locationNodes = locationNodes.reduce((accumulator, locationNode) => {
      if (!locationNode.parentLocationId) {
        accumulator.push(locationNode);
      }
      if (locationNodes.some(({ __instance_id }) => __instance_id === locationNode.parentLocationId)) {
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
