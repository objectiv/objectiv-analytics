/*
 * Copyright 2022 Objectiv B.V.
 */

import { AbstractLocationContext } from '@objectiv/schema';

/**
 * LocationTree nodes have the same shape of LocationContext, but they can have a parent LocationNode themselves.
 */
export type LocationNode = AbstractLocationContext & {
  /**
   * The parent LocationNode identifier.
   */
  parentLocationId: string | null;
};

/**
 * LocationTree is a global object providing a few utility methods to interact with the `locationNodes` global state.
 * LocationContextWrapper makes sure to add new LocationNodes to the tree whenever a Location Wrapper is used.
 */
export interface LocationTreeInterface {
  /**
   * Completely resets LocationTree state. Mainly useful while testing.
   */
  clear: () => void;

  /**
   * Helper method to return a list of children of the given LocationNode
   */
  children: (locationNode: LocationNode) => LocationNode[];

  /**
   * Helper method to log and register an error for the given locationId
   *
   * NOTE: Currently we support only `collision` issues. As more checks are implemented the type parameter may change.
   *
   * `collision` is optional and defaults to 'collision'.
   */
  error: (locationId: string, message: string, type?: 'collision') => void;

  /**
   * Logs a readable version of the `locationNodes` state to the console.
   *
   * `depth` is optional and defaults to 0.
   */
  log: (locationNode?: LocationNode, depth?: number) => void;

  /**
   * Checks the validity of the `locationNodes` state.
   * Currently, we perform only Uniqueness Check: if identical branches are detected they will be logged to the console.
   *
   * Note: This method is invoked automatically when calling `LocationTree.add`.
   *
   * `locationStack` is optional and defaults to [].
   * `locationPaths` is optional and defaults to new Set().
   */
  validate: (
    locationNode?: LocationNode,
    locationStack?: AbstractLocationContext[],
    locationPaths?: Set<string>
  ) => void;

  /**
   * Adds the given LocationContext to the `locationNodes` state, then invokes `LocationTree.validate` to report issues.
   *
   * Note: This method is invoked automatically by LocationContextWrapper.
   * Note: This method automatically invokes `validate`.
   */
  add: (locationContext: AbstractLocationContext, parentLocationContext: AbstractLocationContext | null) => void;

  /**
   * Removes the LocationNode corresponding to the given LocationContext from the LocationTree and errorCache.
   * Performs also a recursive cleanup of orphaned nodes afterwards.
   *
   * Note: This method is invoked automatically by LocationContextWrapper.
   */
  remove: (locationContext: AbstractLocationContext) => void;
}
