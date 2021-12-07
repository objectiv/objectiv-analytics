/*
 * Copyright 2021 Objectiv B.V.
 */

import { TrackerConfig } from '@objectiv/tracker-core';

/**
 * Compares two TrackerConfig objects ignoring mutable attributes.
 * Returns true if configurations are equivalent, false otherwise.
 */
export const compareTrackerConfigs = (trackerConfigA: TrackerConfig, trackerConfigB: TrackerConfig) => {
  // Clone both configurations onto new mutable objects
  let trackerConfigAClone = { ...trackerConfigA };
  let trackerConfigBClone = { ...trackerConfigB };

  // Get rid of mutable attributes
  delete trackerConfigAClone.active;
  delete trackerConfigBClone.active;

  // Compare resulting objects by stringify them
  return JSON.stringify(trackerConfigAClone) === JSON.stringify(trackerConfigBClone);
};
