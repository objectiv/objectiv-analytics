/*
 * Copyright 2021 Objectiv B.V.
 */

import { TrackerConfig } from '@objectiv/tracker-core';

/**
 * Browser Tracker can be configured in a easier way, as opposed to the core tracker, by specifying just an `endpoint`.
 * Internally it will automatically configure the Transport layer for the given `endpoint` with sensible defaults.
 * It also accepts a number of options to configure automatic tracking behavior:
 */
export type BrowserTrackerConfig = TrackerConfig & {
  /**
   * The collector endpoint URL.
   */
  endpoint?: string;

  /**
   * Optional. Whether to track application loaded events automatically. Enabled by default.
   */
  trackApplicationLoaded?: boolean;

  /**
   * Optional. Whether to track URL change events automatically. Enabled by default.
   */
  trackURLChanges?: boolean;
};
