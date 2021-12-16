/*
 * Copyright 2021 Objectiv B.V.
 */

import { makeTrackerDefaultPluginsList } from '@objectiv/tracker-core';
import { ReactTrackerConfig } from '../../ReactTracker';

/**
 * The default list of Plugins of React Tracker
 */
export const makeDefaultPluginsList = (trackerConfig: ReactTrackerConfig) => [
  ...makeTrackerDefaultPluginsList(trackerConfig),
];
