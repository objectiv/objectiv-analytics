import { LocationStack } from './Context';

/**
 * Converts a Location Stack onto its Location Path
 */
export const getLocationPath = (locationStack: LocationStack) => {
  return locationStack.map((context) => `${context._type.replace('Context', '')}:${context.id}`).join(' / ');
};

/**
 * Represents a Location collision. Returned by TrackerState.addElementLocation whenever the uniqueness check fails.
 */
export type LocationCollision = {
  locationPath: string;
  existingElementId: string;
  collidingElementId: string;
};

/**
 * Trackers global state
 */
export const TrackerState = {
  /**
   * An Map of Locations by Elements
   */
  elementLocations: new Map<string, string[]>(),

  /**
   * Clears the state
   */
  clear: () => {
    TrackerState.elementLocations = new Map();
  },

  /**
   * Binds and Element to a specific Location:
   *  - Returns `undefined` if the given Location path is empty
   *  - Binds the Element to the Location and returns `true` if Location uniqueness passes
   *  - Returns `false` if Location uniqueness fails, without updating the state
   */
  addElementLocation: ({
    elementId,
    locationPath,
  }: {
    elementId: string;
    locationPath: string;
  }): true | LocationCollision => {
    // We can't really do any checking without a Location
    if (!locationPath) {
      return true;
    }

    // If a different Element with the same location exists, return false
    for (let [existingElementId, locations] of Array.from(TrackerState.elementLocations.entries())) {
      if (existingElementId !== elementId && locations.includes(locationPath)) {
        return {
          locationPath,
          existingElementId,
          collidingElementId: elementId,
        };
      }
    }

    // Retrieve existingLocations for the given Element
    const existingLocations = TrackerState.elementLocations.get(elementId) ?? [];

    // Store new Location in state, if not already there
    if (!existingLocations.includes(locationPath)) {
      TrackerState.elementLocations.set(elementId, [...existingLocations, locationPath]);
    }

    return true;
  },

  /**
   * Removes an Element from TrackerState. Used when Elements unmount
   */
  removeElement: (elementToRemove: string | undefined) => {
    if (!elementToRemove) {
      return false;
    }

    return TrackerState.elementLocations.delete(elementToRemove);
  },
};
