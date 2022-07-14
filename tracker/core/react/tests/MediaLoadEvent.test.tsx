/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { LocationContextName, makeContentContext, makeMediaLoadEvent, Tracker } from '@objectiv/tracker-core';
import { render } from '@testing-library/react';
import React from 'react';
import { TrackingContextProvider, trackMediaLoadEvent, useMediaLoadEventTracker } from '../src';

describe('trackMediaLoad', () => {
  beforeEach(() => {
    jest.resetAllMocks();
  });

  afterEach(() => {
    jest.resetAllMocks();
  });

  it('should track a MediaLoadEvent (programmatic)', () => {
    const tracker = new Tracker({ applicationId: 'app-id' });
    jest.spyOn(tracker, 'trackEvent');

    trackMediaLoadEvent({ tracker });

    expect(tracker.trackEvent).toHaveBeenCalledTimes(1);
    expect(tracker.trackEvent).toHaveBeenNthCalledWith(1, expect.objectContaining(makeMediaLoadEvent()), undefined);
  });

  it('should track a MediaLoadEvent (hook relying on TrackingContextProvider)', () => {
    const LogTransport = { transportName: 'LogTransport', handle: jest.fn(), isUsable: () => true };
    const tracker = new Tracker({ applicationId: 'app-id', transport: LogTransport });

    const Component = () => {
      const trackMediaLoadEvent = useMediaLoadEventTracker();
      trackMediaLoadEvent();

      return <>Component triggering MediaLoadEvent</>;
    };

    render(
      <TrackingContextProvider tracker={tracker}>
        <Component />
      </TrackingContextProvider>
    );

    expect(LogTransport.handle).toHaveBeenCalledTimes(1);
    expect(LogTransport.handle).toHaveBeenNthCalledWith(1, expect.objectContaining({ _type: 'MediaLoadEvent' }));
  });

  it('should track a MediaLoadEvent (hook with custom tracker and location)', () => {
    const tracker = new Tracker({ applicationId: 'app-id' });
    jest.spyOn(tracker, 'trackEvent');

    const customTracker = new Tracker({ applicationId: 'app-id-2' });
    jest.spyOn(customTracker, 'trackEvent');

    const Component = () => {
      const trackMediaLoadEvent = useMediaLoadEventTracker({
        tracker: customTracker,
        locationStack: [makeContentContext({ id: 'override' })],
      });
      trackMediaLoadEvent();

      return <>Component triggering MediaLoadEvent</>;
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
        makeMediaLoadEvent({
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
