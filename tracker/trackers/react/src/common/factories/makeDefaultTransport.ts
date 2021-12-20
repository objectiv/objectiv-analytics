/*
 * Copyright 2021 Objectiv B.V.
 */

import { TrackerTransportInterface, TrackerTransportRetry, TrackerTransportSwitch } from '@objectiv/tracker-core';
import { FetchTransport } from '@objectiv/transport-fetch';
import { XHRTransport } from '@objectiv/transport-xhr';
import { ReactTrackerConfig } from '../../ReactTracker';

/**
 * A factory to create the default Transport of Browser Tracker.
 */
export const makeDefaultTransport = (trackerConfig: ReactTrackerConfig): TrackerTransportInterface =>
  new TrackerTransportRetry({
    console: trackerConfig.console,
    transport: new TrackerTransportSwitch({
      console: trackerConfig.console,
      transports: [
        new FetchTransport({ endpoint: trackerConfig.endpoint, console: trackerConfig.console }),
        new XHRTransport({ endpoint: trackerConfig.endpoint, console: trackerConfig.console }),
      ],
    }),
  });
