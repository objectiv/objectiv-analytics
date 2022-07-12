/*
 * Copyright 2022 Objectiv B.V.
 */

import { ApplicationContextPlugin } from '@objectiv/plugin-application-context';
import { TrackerPluginInterface } from '@objectiv/tracker-core';
import { ReactNativeTrackerConfig } from '@objectiv/tracker-react-native';

/**
 * The default list of Plugins of React Native Tracker
 */
export const makeReactNativeTrackerDefaultPluginsList = (trackerConfig: ReactNativeTrackerConfig) => {
  const { trackApplicationContext = true } = trackerConfig;

  const plugins: TrackerPluginInterface[] = [];

  if (trackApplicationContext) {
    plugins.push(new ApplicationContextPlugin());
  }

  return plugins;
};
