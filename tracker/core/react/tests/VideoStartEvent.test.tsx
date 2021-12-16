/*
 * Copyright 2021 Objectiv B.V.
 */

import { makeVideoStartEvent, Tracker } from '@objectiv/tracker-core';
import { render } from '@testing-library/react';
import { makeSectionContext, TrackingContextProvider, trackVideoStartEvent, useVideoStartEventTracker } from '../src';

describe('trackVideoStart', () => {
  beforeEach(() => {
    jest.resetAllMocks();
  });

  afterEach(() => {
    jest.resetAllMocks();
  });

  it('should track a VideoStartEvent', () => {
    const tracker = new Tracker({ applicationId: 'app-id' });
    jest.spyOn(tracker, 'trackEvent');

    trackVideoStartEvent({ tracker });

    expect(tracker.trackEvent).toHaveBeenCalledTimes(1);
    expect(tracker.trackEvent).toHaveBeenNthCalledWith(1, expect.objectContaining(makeVideoStartEvent()), undefined);
  });

  it('should track a VideoStartEvent (hook relying on TrackingContextProvider)', () => {
    const spyTransport = { transportName: 'SpyTransport', handle: jest.fn(), isUsable: () => true };
    const tracker = new Tracker({ applicationId: 'app-id', transport: spyTransport });

    const Component = () => {
      const trackVideoStartEvent = useVideoStartEventTracker();
      trackVideoStartEvent();

      return <>Component triggering VideoStartEvent</>;
    };

    render(
      <TrackingContextProvider tracker={tracker}>
        <Component />
      </TrackingContextProvider>
    );

    expect(spyTransport.handle).toHaveBeenCalledTimes(1);
    expect(spyTransport.handle).toHaveBeenNthCalledWith(1, expect.objectContaining({ _type: 'VideoStartEvent' }));
  });

  it('should track a VideoStartEvent (hook with custom tracker and location)', () => {
    const tracker = new Tracker({ applicationId: 'app-id' });
    jest.spyOn(tracker, 'trackEvent');

    const customTracker = new Tracker({ applicationId: 'app-id-2' });
    jest.spyOn(customTracker, 'trackEvent');

    const Component = () => {
      const trackVideoStartEvent = useVideoStartEventTracker({
        tracker: customTracker,
        locationStack: [makeSectionContext({ id: 'override' })],
      });
      trackVideoStartEvent();

      return <>Component triggering VideoStartEvent</>;
    };

    const location1 = makeSectionContext({ id: 'root' });
    const location2 = makeSectionContext({ id: 'child' });

    render(
      <TrackingContextProvider tracker={tracker} locationStack={[location1, location2]}>
        <Component />
      </TrackingContextProvider>
    );

    expect(tracker.trackEvent).not.toHaveBeenCalled();
    expect(customTracker.trackEvent).toHaveBeenCalledTimes(1);
    expect(customTracker.trackEvent).toHaveBeenNthCalledWith(
      1,
      expect.objectContaining(
        makeVideoStartEvent({
          location_stack: [expect.objectContaining({ _type: 'SectionContext', id: 'override' })],
        })
      ),
      undefined
    );
  });
});
