/*
 * Copyright 2021 Objectiv B.V.
 */

import { TrackerRepository } from '@objectiv/tracker-core';
import { BrowserTracker } from '../BrowserTracker';
import { windowExists } from './windowExists';

/**
 * Window extension for our namespace
 */
declare global {
  interface Window {
    objectiv: {
      trackers: TrackerRepository<BrowserTracker>;
    };
  }
}

/**
 * Initialize window global namespace, unless already existing
 */
if (windowExists()) {
  window.objectiv = window.objectiv || {
    trackers: new TrackerRepository(),
  };
}
