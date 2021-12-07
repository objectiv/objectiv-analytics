/*
 * Copyright 2021 Objectiv B.V.
 */

import { WebDocumentContextPlugin } from '@objectiv/plugin-web-document-context';
import { makeTrackerDefaultPluginsList } from '@objectiv/tracker-core';
import { BrowserTrackerConfig } from '../../definitions/BrowserTrackerConfig';

/**
 * The default list of Plugins of Browser Tracker
 */
export const makeDefaultPluginsList = (trackerConfig: BrowserTrackerConfig) => [
  ...makeTrackerDefaultPluginsList(trackerConfig),
  new WebDocumentContextPlugin({ console: trackerConfig.console }),
];
