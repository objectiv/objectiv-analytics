/*
 * Copyright 2021 Objectiv B.V.
 */

import { makeAbortedEvent, Tracker } from '@objectiv/tracker-core';
import { render } from '@testing-library/react';
import { makeSectionContext, trackAbortedEvent, TrackingContextProvider, useAbortedEventTracker } from '../src';

describe('AbortedEvent', () => {
  beforeEach(() => {
    jest.resetAllMocks();
  });

  afterEach(() => {
    jest.resetAllMocks();
  });

  it('should track an AbortedEvent (programmatic)', () => {
    const tracker = new Tracker({ applicationId: 'app-id' });
    jest.spyOn(tracker, 'trackEvent');

    trackAbortedEvent({ tracker });

    expect(tracker.trackEvent).toHaveBeenCalledTimes(1);
    expect(tracker.trackEvent).toHaveBeenNthCalledWith(1, expect.objectContaining(makeAbortedEvent()), undefined);
  });

  it('should track an AbortedEvent (hook relying on TrackingContextProvider)', () => {
    const spyTransport = { transportName: 'SpyTransport', handle: jest.fn(), isUsable: () => true };
    const tracker = new Tracker({ applicationId: 'app-id', transport: spyTransport });

    const Component = () => {
      const trackAbortedEvent = useAbortedEventTracker();
      trackAbortedEvent();

      return <>Component triggering AbortedEvent</>;
    };

    render(
      <TrackingContextProvider tracker={tracker}>
        <Component />
      </TrackingContextProvider>
    );

    expect(spyTransport.handle).toHaveBeenCalledTimes(1);
    expect(spyTransport.handle).toHaveBeenNthCalledWith(1, expect.objectContaining({ _type: 'AbortedEvent' }));
  });

  it('should track an AbortedEvent (hook with custom tracker and location)', () => {
    const tracker = new Tracker({ applicationId: 'app-id' });
    jest.spyOn(tracker, 'trackEvent');

    const customTracker = new Tracker({ applicationId: 'app-id-2' });
    jest.spyOn(customTracker, 'trackEvent');

    const Component = () => {
      const trackAbortedEvent = useAbortedEventTracker({
        tracker: customTracker,
        locationStack: [makeSectionContext({ id: 'override' })],
      });
      trackAbortedEvent();

      return <>Component triggering AbortedEvent</>;
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
        makeAbortedEvent({ location_stack: [expect.objectContaining({ _type: 'SectionContext', id: 'override' })] })
      ),
      undefined
    );
  });
});
