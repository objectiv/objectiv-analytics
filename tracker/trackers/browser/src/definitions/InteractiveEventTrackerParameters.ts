/*
 * Copyright 2021 Objectiv B.V.
 */

import { GlobalContexts, LocationStack } from '@objectiv/tracker-core';
import { BrowserTracker } from '../BrowserTracker';
import { TrackedElement } from './TrackedElement';
import { TrackerErrorHandlerCallback } from './TrackerErrorHandlerCallback';

/**
 * The parameters of the Event Tracker shorthand functions
 */
export type InteractiveEventTrackerParameters = {
  element: TrackedElement;
  locationStack?: LocationStack;
  globalContexts?: GlobalContexts;
  tracker?: BrowserTracker;
  onError?: TrackerErrorHandlerCallback;
};
