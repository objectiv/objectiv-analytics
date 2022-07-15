/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { LocationContextName, makeContentContext, makeNonInteractiveEvent, Tracker } from '@objectiv/tracker-core';
import { render } from '@testing-library/react';
import React from 'react';
import { TrackingContextProvider, trackNonInteractiveEvent, useNonInteractiveEventTracker } from '../src';

describe('NonInteractiveEvent', () => {
  beforeEach(() => {
    jest.resetAllMocks();
  });

  afterEach(() => {
    jest.resetAllMocks();
  });

  it('should track an NonInteractiveEvent (programmatic)', () => {
    const tracker = new Tracker({ applicationId: 'app-id' });
    jest.spyOn(tracker, 'trackEvent');

    trackNonInteractiveEvent({ tracker });

    expect(tracker.trackEvent).toHaveBeenCalledTimes(1);
    expect(tracker.trackEvent).toHaveBeenNthCalledWith(
      1,
      expect.objectContaining(makeNonInteractiveEvent()),
      undefined
    );
  });

  it('should track an NonInteractiveEvent (hook relying on TrackingContextProvider)', () => {
    const LogTransport = { transportName: 'LogTransport', handle: jest.fn(), isUsable: () => true };
    const tracker = new Tracker({ applicationId: 'app-id', transport: LogTransport });

    const Component = () => {
      const trackNonInteractiveEvent = useNonInteractiveEventTracker();
      trackNonInteractiveEvent();

      return <>Component triggering NonInteractiveEvent</>;
    };

    render(
      <TrackingContextProvider tracker={tracker}>
        <Component />
      </TrackingContextProvider>
    );

    expect(LogTransport.handle).toHaveBeenCalledTimes(1);
    expect(LogTransport.handle).toHaveBeenNthCalledWith(1, expect.objectContaining({ _type: 'NonInteractiveEvent' }));
  });

  it('should track an NonInteractiveEvent (hook with custom tracker and location)', () => {
    const tracker = new Tracker({ applicationId: 'app-id' });
    jest.spyOn(tracker, 'trackEvent');

    const customTracker = new Tracker({ applicationId: 'app-id-2' });
    jest.spyOn(customTracker, 'trackEvent');

    const Component = () => {
      const trackNonInteractiveEvent = useNonInteractiveEventTracker({
        tracker: customTracker,
        locationStack: [makeContentContext({ id: 'override' })],
      });
      trackNonInteractiveEvent();

      return <>Component triggering NonInteractiveEvent</>;
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
        makeNonInteractiveEvent({
          location_stack: [
            expect.objectContaining({ _type: location1._type, id: location1.id }),
            expect.objectContaining({ _type: location2._type, id: location2.id }),
            expect.objectContaining({ _type: LocationContextName.ContentContext, id: 'override' }),
          ],
        })
      ),
      undefined
    );
  });
});
