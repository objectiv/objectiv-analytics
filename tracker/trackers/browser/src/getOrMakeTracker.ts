/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { BrowserTracker } from './BrowserTracker';
import { compareTrackerConfigs } from './common/compareTrackerConfigs';
import { BrowserTrackerConfig } from './definitions/BrowserTrackerConfig';
import { getTrackerRepository } from './getTrackerRepository';
import { makeTracker } from './makeTracker';

/**
 * Retrieves a specific Tracker's instance from the TrackerRepository or creates one if it doesn't exist yet.
 * Logs an error to console if the given Tracker ID exists but its configuration doesn't match the given one.
 */
export const getOrMakeTracker = (trackerConfig: BrowserTrackerConfig): BrowserTracker => {
  // Get the TrackerRepository
  const trackerRepository = getTrackerRepository();

  // Determine trackerId
  const trackerId = trackerConfig.trackerId ?? trackerConfig.applicationId;

  // Attempt to retrieve tracker from Repository map, low-level to not trigger any console messages
  const tracker = trackerRepository.trackersMap.get(trackerId);

  // If we did not find a tracker, make a new one.
  if (!tracker) {
    return makeTracker(trackerConfig);
  }

  // We found a Tracker instance but, before returning it, ensure its config matches the given configuration
  if (!compareTrackerConfigs(tracker.trackerConfig, trackerConfig)) {
    globalThis.objectiv.devTools?.TrackerConsole.error(
      `Tracker \`${trackerId}\` exists but its configuration doesn't match the given one. This means getOrMakeTracker has been called twice with different configs.`
    );
  }

  return tracker;
};
