/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { TrackerConfig } from '@objectiv/tracker-core';

/**
 * Browser Tracker can be configured in a easier way, as opposed to the core tracker, by specifying just an `endpoint`.
 * Internally it will automatically configure the Transport layer for the given `endpoint` with sensible defaults.
 * It also accepts a number of options to configure automatic tracking behavior:
 */
export type BrowserTrackerConfig = Omit<TrackerConfig, 'platform'> & {
  /**
   * The collector endpoint URL.
   */
  endpoint?: string;

  /**
   * Optional. Whether to track application loaded events automatically. Enabled by default.
   */
  trackApplicationLoadedEvent?: boolean;

  /**
   * Optional. Whether to track ApplicationContext automatically. Enabled by default.
   */
  trackApplicationContext?: boolean;

  /**
   * Optional. Whether to automatically create HttpContext based on Document and Navigation APIs. Enabled by default.
   */
  trackHttpContext?: boolean;

  /**
   * Optional. Whether to automatically create PathContext based on URLs. Enabled by default.
   */
  trackPathContextFromURL?: boolean;

  /**
   * Optional. Whether to automatically create RootLocationContext based on URLs first slugs. Enabled by default.
   */
  trackRootLocationContextFromURL?: boolean;
};
