/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import '@objectiv/developer-tools';
import { MockConsoleImplementation, LogTransport } from '@objectiv/testing-tools';
import { generateGUID } from '@objectiv/tracker-core';
import {
  AutoTrackingState,
  BrowserTracker,
  getTracker,
  makeTracker,
  startAutoTracking,
  stopAutoTracking,
} from '../src';

require('@objectiv/developer-tools');
globalThis.objectiv.devTools?.TrackerConsole.setImplementation(MockConsoleImplementation);

describe('startAutoTracking', () => {
  beforeEach(() => {
    jest.resetAllMocks();
    makeTracker({ applicationId: generateGUID(), endpoint: 'test' });
    expect(getTracker()).toBeInstanceOf(BrowserTracker);
    jest.spyOn(getTracker(), 'trackEvent');
  });

  it('options', () => {
    startAutoTracking({ trackApplicationLoadedEvent: false });
    stopAutoTracking();
    startAutoTracking({ trackApplicationLoadedEvent: true });
    stopAutoTracking();
    startAutoTracking({ trackApplicationLoadedEvent: false });
    stopAutoTracking();
    startAutoTracking({});
    stopAutoTracking();
    startAutoTracking();
    stopAutoTracking();
    stopAutoTracking();
  });

  it('should TrackerConsole.error', () => {
    startAutoTracking();
    expect(MockConsoleImplementation.error).not.toHaveBeenCalled();
    // @ts-ignore
    AutoTrackingState.observerInstance = {
      disconnect: () => {
        throw new Error('oops');
      },
    };
    stopAutoTracking();
    expect(MockConsoleImplementation.error).toHaveBeenCalledTimes(1);
  });

  it('should not track application loaded event', () => {
    const tracker = new BrowserTracker({ transport: new LogTransport(), applicationId: 'app' });
    jest.spyOn(tracker, 'trackEvent');

    startAutoTracking({ trackApplicationLoadedEvent: false });

    expect(tracker.trackEvent).not.toHaveBeenCalled();
  });
});
