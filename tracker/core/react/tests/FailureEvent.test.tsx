/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { LocationContextName, makeContentContext, makeFailureEvent, Tracker } from '@objectiv/tracker-core';
import { render } from '@testing-library/react';
import React from 'react';
import { trackFailureEvent, TrackingContextProvider, useFailureEventTracker } from '../src';

describe('FailureEvent', () => {
  beforeEach(() => {
    jest.resetAllMocks();
  });

  afterEach(() => {
    jest.resetAllMocks();
  });

  it('should track an FailureEvent (programmatic)', () => {
    const tracker = new Tracker({ applicationId: 'app-id' });
    jest.spyOn(tracker, 'trackEvent');

    trackFailureEvent({ tracker, message: 'ko' });

    expect(tracker.trackEvent).toHaveBeenCalledTimes(1);
    expect(tracker.trackEvent).toHaveBeenNthCalledWith(
      1,
      expect.objectContaining(makeFailureEvent({ message: 'ko' })),
      undefined
    );
  });

  it('should track an FailureEvent (hook relying on TrackingContextProvider)', () => {
    const LogTransport = { transportName: 'LogTransport', handle: jest.fn(), isUsable: () => true };
    const tracker = new Tracker({ applicationId: 'app-id', transport: LogTransport });

    const Component = () => {
      const trackFailureEvent = useFailureEventTracker();
      trackFailureEvent({ message: 'ko' });

      return <>Component triggering FailureEvent</>;
    };

    render(
      <TrackingContextProvider tracker={tracker}>
        <Component />
      </TrackingContextProvider>
    );

    expect(LogTransport.handle).toHaveBeenCalledTimes(1);
    expect(LogTransport.handle).toHaveBeenNthCalledWith(1, expect.objectContaining({ _type: 'FailureEvent' }));
  });

  it('should track an FailureEvent (hook with custom tracker and location)', () => {
    const tracker = new Tracker({ applicationId: 'app-id' });
    jest.spyOn(tracker, 'trackEvent');

    const customTracker = new Tracker({ applicationId: 'app-id-2' });
    jest.spyOn(customTracker, 'trackEvent');

    const Component = () => {
      const trackFailureEvent = useFailureEventTracker({
        tracker: customTracker,
        locationStack: [makeContentContext({ id: 'override' })],
      });
      trackFailureEvent({ message: 'ko' });

      return <>Component triggering FailureEvent</>;
    };

    const location1 = makeContentContext({ id: 'root' });
    const location2 = makeContentContext({ id: 'child' });

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
        makeFailureEvent({
          message: 'ko',
          location_stack: [expect.objectContaining({ _type: LocationContextName.ContentContext, id: 'override' })],
        })
      ),
      undefined
    );
  });
});
