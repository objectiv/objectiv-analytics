/*
 * Copyright 2021 Objectiv B.V.
 */

import { Tracker } from '@objectiv/tracker-core';
import { createContext } from 'react';

/**
 * TrackerProviderContext state has only one attribute holding an instance of the Tracker.
 */
export type TrackerProviderContext = {
  /**
   * A Tracker instance.
   */
  tracker: Tracker;
};

/**
 * A Context to retrieve a Tracker instance.
 * Components may retrieve their Tracker either via `useContext(TrackerContext)` or `useTracker()`.
 */
export const TrackerProviderContext = createContext<null | TrackerProviderContext>(null);
