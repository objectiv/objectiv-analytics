/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { LocationContextName, makeContentContext, makeSuccessEvent, Tracker } from '@objectiv/tracker-core';
import { render } from '@testing-library/react';
import React from 'react';
import { TrackingContextProvider, trackSuccessEvent, useSuccessEventTracker } from '../src';

describe('SuccessEvent', () => {
  beforeEach(() => {
    jest.resetAllMocks();
  });

  afterEach(() => {
    jest.resetAllMocks();
  });

  it('should track a SuccessEvent (programmatic)', () => {
    const tracker = new Tracker({ applicationId: 'app-id' });
    jest.spyOn(tracker, 'trackEvent');

    trackSuccessEvent({ tracker, message: 'ok' });

    expect(tracker.trackEvent).toHaveBeenCalledTimes(1);
    expect(tracker.trackEvent).toHaveBeenNthCalledWith(
      1,
      expect.objectContaining(makeSuccessEvent({ message: 'ok' })),
      undefined
    );
  });

  it('should track a SuccessEvent (hook relying on TrackingContextProvider)', () => {
    const spyTransport = { transportName: 'SpyTransport', handle: jest.fn(), isUsable: () => true };
    const tracker = new Tracker({ applicationId: 'app-id', transport: spyTransport });

    const Component = () => {
      const trackSuccessEvent = useSuccessEventTracker();
      trackSuccessEvent({ message: 'ok' });

      return <>Component triggering SuccessEvent</>;
    };

    render(
      <TrackingContextProvider tracker={tracker}>
        <Component />
      </TrackingContextProvider>
    );

    expect(spyTransport.handle).toHaveBeenCalledTimes(1);
    expect(spyTransport.handle).toHaveBeenNthCalledWith(1, expect.objectContaining({ _type: 'SuccessEvent' }));
  });

  it('should track a SuccessEvent (hook with custom tracker)', () => {
    const tracker = new Tracker({ applicationId: 'app-id' });
    jest.spyOn(tracker, 'trackEvent');

    const customTracker = new Tracker({ applicationId: 'app-id-2' });
    jest.spyOn(customTracker, 'trackEvent');

    const Component = () => {
      const trackSuccessEvent = useSuccessEventTracker({
        tracker: customTracker,
        locationStack: [makeContentContext({ id: 'override' })],
      });
      trackSuccessEvent({ message: 'ok' });

      return <>Component triggering SuccessEvent</>;
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
        makeSuccessEvent({
          message: 'ok',
          location_stack: [expect.objectContaining({ _type: LocationContextName.ContentContext, id: 'override' })],
        })
      ),
      undefined
    );
  });
});
