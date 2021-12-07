/*
 * Copyright 2021 Objectiv B.V.
 */

import { TrackerTransportInterface, TrackerTransportRetry, TrackerTransportSwitch } from '@objectiv/tracker-core';
import { BrowserTrackerConfig } from '../../definitions/BrowserTrackerConfig';
import { FetchAPITransport } from '../../transports/FetchAPITransport';
import { XMLHttpRequestTransport } from '../../transports/XMLHttpRequestTransport';

/**
 * A factory to create the default Transport of Browser Tracker.
 */
export const makeDefaultTransport = (trackerConfig: BrowserTrackerConfig): TrackerTransportInterface =>
  new TrackerTransportRetry({
    console: trackerConfig.console,
    transport: new TrackerTransportSwitch({
      console: trackerConfig.console,
      transports: [
        new FetchAPITransport({ endpoint: trackerConfig.endpoint, console: trackerConfig.console }),
        new XMLHttpRequestTransport({ endpoint: trackerConfig.endpoint, console: trackerConfig.console }),
      ],
    }),
  });
