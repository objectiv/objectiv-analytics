/*
 * Copyright 2021 Objectiv B.V.
 */

import { makeVideoPauseEvent, Tracker } from '@objectiv/tracker-core';
import { render } from '@testing-library/react';
import { makeSectionContext, TrackingContextProvider, trackVideoPauseEvent, useVideoPauseEventTracker } from '../src';

describe('trackVideoPause', () => {
  beforeEach(() => {
    jest.resetAllMocks();
  });

  afterEach(() => {
    jest.resetAllMocks();
  });

  it('should track a VideoPauseEvent (programmatic)', () => {
    const tracker = new Tracker({ applicationId: 'app-id' });
    jest.spyOn(tracker, 'trackEvent');

    trackVideoPauseEvent({ tracker });

    expect(tracker.trackEvent).toHaveBeenCalledTimes(1);
    expect(tracker.trackEvent).toHaveBeenNthCalledWith(1, expect.objectContaining(makeVideoPauseEvent()), undefined);
  });

  it('should track a VideoPauseEvent (hook relying on TrackingContextProvider)', () => {
    const spyTransport = { transportName: 'SpyTransport', handle: jest.fn(), isUsable: () => true };
    const tracker = new Tracker({ applicationId: 'app-id', transport: spyTransport });

    const Component = () => {
      const trackVideoPauseEvent = useVideoPauseEventTracker();
      trackVideoPauseEvent();

      return <>Component triggering VideoPauseEvent</>;
    };

    render(
      <TrackingContextProvider tracker={tracker}>
        <Component />
      </TrackingContextProvider>
    );

    expect(spyTransport.handle).toHaveBeenCalledTimes(1);
    expect(spyTransport.handle).toHaveBeenNthCalledWith(1, expect.objectContaining({ _type: 'VideoPauseEvent' }));
  });

  it('should track a VideoPauseEvent (hook with custom tracker and location)', () => {
    const tracker = new Tracker({ applicationId: 'app-id' });
    jest.spyOn(tracker, 'trackEvent');

    const customTracker = new Tracker({ applicationId: 'app-id-2' });
    jest.spyOn(customTracker, 'trackEvent');

    const Component = () => {
      const trackVideoPauseEvent = useVideoPauseEventTracker({
        tracker: customTracker,
        locationStack: [makeSectionContext({ id: 'override' })],
      });
      trackVideoPauseEvent();

      return <>Component triggering VideoPauseEvent</>;
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
        makeVideoPauseEvent({
          location_stack: [expect.objectContaining({ _type: 'SectionContext', id: 'override' })],
        })
      ),
      undefined
    );
  });
});
