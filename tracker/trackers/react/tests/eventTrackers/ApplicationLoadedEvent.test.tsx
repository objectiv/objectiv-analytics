/*
 * Copyright 2021 Objectiv B.V.
 */

import { makeApplicationLoadedEvent, makeURLChangeEvent } from '@objectiv/tracker-core';
import { render } from '@testing-library/react';
import {
  ObjectivProvider,
  ReactTracker,
  trackApplicationLoadedEvent,
  TrackerProvider,
  useApplicationLoadedEventTracker,
} from '../../src';

describe('trackApplicationLoaded', () => {
  beforeEach(() => {
    jest.resetAllMocks();
  });

  afterEach(() => {
    jest.resetAllMocks();
  });

  it('should track an ApplicationLoadedEvent (automatically by ObjectivProvider)', () => {
    const tracker = new ReactTracker({ applicationId: 'app-id' });
    jest.spyOn(tracker, 'trackEvent');

    render(<ObjectivProvider tracker={tracker}>app</ObjectivProvider>);

    expect(tracker.trackEvent).toHaveBeenCalledTimes(2);
    expect(tracker.trackEvent).toHaveBeenNthCalledWith(1, expect.objectContaining(makeApplicationLoadedEvent()));
    expect(tracker.trackEvent).toHaveBeenNthCalledWith(2, expect.objectContaining(makeURLChangeEvent()));
  });

  it('should track an ApplicationLoadedEvent (programmatic)', () => {
    const tracker = new ReactTracker({ applicationId: 'app-id' });
    jest.spyOn(tracker, 'trackEvent');

    trackApplicationLoadedEvent({ tracker });

    expect(tracker.trackEvent).toHaveBeenCalledTimes(1);
    expect(tracker.trackEvent).toHaveBeenNthCalledWith(1, expect.objectContaining(makeApplicationLoadedEvent()));
  });

  it('should track an ApplicationLoadedEvent (hook relying on ObjectivProvider)', () => {
    const spyTransport = { transportName: 'SpyTransport', handle: jest.fn(), isUsable: () => true };
    const tracker = new ReactTracker({ applicationId: 'app-id', transport: spyTransport });

    const Component = () => {
      const trackApplicationLoaded = useApplicationLoadedEventTracker();
      trackApplicationLoaded();

      return <>Component triggering Application Loaded</>;
    };

    render(
      <TrackerProvider tracker={tracker}>
        <Component />
      </TrackerProvider>
    );

    expect(spyTransport.handle).toHaveBeenCalledTimes(1);
    expect(spyTransport.handle).toHaveBeenNthCalledWith(
      1,
      expect.objectContaining({ _type: 'ApplicationLoadedEvent' })
    );
  });

  it('should track an ApplicationLoadedEvent (hook with custom tracker)', () => {
    const tracker = new ReactTracker({ applicationId: 'app-id' });
    jest.spyOn(tracker, 'trackEvent');

    const customTracker = new ReactTracker({ applicationId: 'app-id-2' });
    jest.spyOn(customTracker, 'trackEvent');

    const Component = () => {
      const trackApplicationLoaded = useApplicationLoadedEventTracker(customTracker);
      trackApplicationLoaded();

      return <>Component triggering Application Loaded</>;
    };

    render(
      <TrackerProvider tracker={tracker}>
        <Component />
      </TrackerProvider>
    );

    expect(tracker.trackEvent).not.toHaveBeenCalled();
    expect(customTracker.trackEvent).toHaveBeenCalledTimes(1);
    expect(customTracker.trackEvent).toHaveBeenNthCalledWith(1, expect.objectContaining(makeApplicationLoadedEvent()));
  });
});
