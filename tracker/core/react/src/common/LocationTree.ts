/*
 * Copyright 2021 Objectiv B.V.
 */

import { AbstractLocationContext } from '@objectiv/schema';
import { getLocationPath } from '@objectiv/tracker-core';
import { LocationContext } from '../types';

/**
 * LocationTree nodes have the same shape of LocationContext but they can have children LocationNodes themselves.
 */
export type LocationNode = LocationContext<AbstractLocationContext> & {
  /**
   * An array of LocationNode objects, which may contain more children themselves.
   */
  children: LocationNode[];
};

/**
 * LocationTree root node has `id`, `_type` and `__location_id` hardcoded to null. It's just a container.
 */
export type LocationRootNode = {
  /**
   * LocationRootNode id can only be null.
   */
  id: null;

  /**
   * LocationRootNode _type can only be null.
   */
  _type: null;

  /**
   * LocationRootNode __location_id can only be null.
   */
  __location_id: null;

  /**
   * An array of LocationNode objects, which may contain more children themselves.
   */
  children: LocationNode[];
};

/**
 * Internal state to hold the complete known LocationTree.
 * Each node, exception made for the root one, is a uniquely identifiable Location Context.
 * All nodes may have children LocationNodes.
 */
const locationTree: LocationRootNode = {
  id: null,
  _type: null,
  __location_id: null,
  children: [],
};

/**
 * Internal state to keep track of which identifiers are already known for a certain issue. This is used to prevent
 * notifying the developer of the same issues multiple times.
 *
 * NOTE: Currently we support only `collision` issues. As more checks are implemented this Map may change.
 */
const errorCache = new Map<string, 'collision'>();

/**
 * LocationTree is a global object providing a few utility methods to interact with the `locationTree` global state.
 * LocationContextWrapper makes sure to add new LocationNodes to the tree whenever a Location Wrapper is used.
 */
export const LocationTree = {
  /**
   * completely resets LocationTree state. Mainly useful while testing.
   */
  clear: () => {
    locationTree.children = [];
    errorCache.clear();
  },

  /**
   * Logs a readable version of the `locationTree` state to the console
   */
  log: (locationNode: LocationNode | LocationRootNode = locationTree, depth = 0) => {
    if (!locationNode) {
      return;
    }

    // Only log nodes with _type and id, this leaves out the LocationRootNode node
    if (locationNode._type && locationNode.id) {
      console.log('  '.repeat(depth) + locationNode._type + ':' + locationNode.id);
    }

    depth++;

    locationNode.children.forEach((locationChildNode) => LocationTree.log(locationChildNode, depth));
  },

  /**
   * Finds a node by its id recursively. Returns `null` if a node cannot be found with the given identifier.
   * A starting node, other than the whole `locationTree` state, can be specified.
   */
  findByLocationId: (
    locationId: string | null,
    locationNode: LocationNode | LocationRootNode = locationTree
  ): null | LocationNode | LocationRootNode => {
    if (locationNode.__location_id === locationId) {
      return locationNode;
    }

    let result: null | LocationNode | LocationRootNode = null;

    for (let i = 0; result === null && i < locationNode.children.length; i++) {
      result = LocationTree.findByLocationId(locationId, locationNode.children[i]);
    }

    return result;
  },

  /**
   * Checks the validity of the `locationTree` state.
   * Currently we perform only Uniqueness Check: if identical branches are detected they will be logged to the console.
   *
   * Note: This method is invoked automatically when calling `LocationTree.add`.
   */
  validate: (
    locationNode: LocationNode | LocationRootNode = locationTree,
    locationStack: AbstractLocationContext[] = [],
    locationPaths: Set<string> = new Set()
  ) => {
    // Only push nodes with _type and id, this leaves out the LocationRootNode node
    if (locationNode._type && locationNode.id) {
      locationStack.push(locationNode);
    }

    // Collision detection
    const locationPath = getLocationPath(locationStack);
    const locationPathsSize = locationPaths.size;
    locationPaths.add(locationPath);

    if (locationPathsSize === locationPaths.size && errorCache.get(locationPath) !== 'collision') {
      console.error(`｢objectiv｣ Location collision detected: ${locationPath}`);
      console.log(`Location Tree:`);
      LocationTree.log();
      errorCache.set(locationPath, 'collision');
    }

    // Rerun validation for each child
    locationNode.children.map((childLocationNode) =>
      LocationTree.validate(childLocationNode, [...locationStack], locationPaths)
    );
  },

  /**
   * Adds the given LocationContext to the `locationTree` state, then invokes `LocationTree.validate` to report issues.
   *
   * Note: This method is invoked automatically by LocationContextWrapper.
   */
  add: (
    locationContext: LocationContext<AbstractLocationContext>,
    parentLocation?: LocationContext<AbstractLocationContext>
  ) => {
    const parentLocationNode = LocationTree.findByLocationId(parentLocation?.__location_id ?? null);
    if (!parentLocationNode) {
      throw new Error('Parent LocationNode not found.');
    }

    parentLocationNode.children.push({ ...locationContext, children: [] });

    LocationTree.validate();
  },
};
