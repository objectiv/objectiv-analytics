/*
 * Copyright 2021 Objectiv B.V.
 */

import { makeCompletedEvent, Tracker } from '@objectiv/tracker-core';
import { render } from '@testing-library/react';
import { makeSectionContext, trackCompletedEvent, TrackingContextProvider, useCompletedEventTracker } from '../src';

describe('CompletedEvent', () => {
  beforeEach(() => {
    jest.resetAllMocks();
  });

  afterEach(() => {
    jest.resetAllMocks();
  });

  it('should track a CompletedEvent (programmatic)', () => {
    const tracker = new Tracker({ applicationId: 'app-id' });
    jest.spyOn(tracker, 'trackEvent');

    trackCompletedEvent({ tracker });

    expect(tracker.trackEvent).toHaveBeenCalledTimes(1);
    expect(tracker.trackEvent).toHaveBeenNthCalledWith(1, expect.objectContaining(makeCompletedEvent()), undefined);
  });

  it('should track a CompletedEvent (hook relying on TrackingContextProvider)', () => {
    const spyTransport = { transportName: 'SpyTransport', handle: jest.fn(), isUsable: () => true };
    const tracker = new Tracker({ applicationId: 'app-id', transport: spyTransport });

    const Component = () => {
      const trackCompletedEvent = useCompletedEventTracker();
      trackCompletedEvent();

      return <>Component triggering CompletedEvent</>;
    };

    render(
      <TrackingContextProvider tracker={tracker}>
        <Component />
      </TrackingContextProvider>
    );

    expect(spyTransport.handle).toHaveBeenCalledTimes(1);
    expect(spyTransport.handle).toHaveBeenNthCalledWith(1, expect.objectContaining({ _type: 'CompletedEvent' }));
  });

  it('should track a CompletedEvent (hook with custom tracker)', () => {
    const tracker = new Tracker({ applicationId: 'app-id' });
    jest.spyOn(tracker, 'trackEvent');

    const customTracker = new Tracker({ applicationId: 'app-id-2' });
    jest.spyOn(customTracker, 'trackEvent');

    const Component = () => {
      const trackCompletedEvent = useCompletedEventTracker({
        tracker: customTracker,
        locationStack: [makeSectionContext({ id: 'override' })],
      });
      trackCompletedEvent();

      return <>Component triggering CompletedEvent</>;
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
        makeCompletedEvent({
          location_stack: [expect.objectContaining({ _type: 'SectionContext', id: 'override' })],
        })
      ),
      undefined
    );
  });
});
