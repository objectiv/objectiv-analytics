/*
 * Copyright 2021 Objectiv B.V.
 */

import { makeApplicationLoadedEvent, Tracker } from '@objectiv/tracker-core';
import { render } from '@testing-library/react';
import {
  makeSectionContext,
  ObjectivProvider,
  trackApplicationLoadedEvent,
  TrackingContextProvider,
  useApplicationLoadedEventTracker,
} from '../src';

describe('trackApplicationLoaded', () => {
  beforeEach(() => {
    jest.resetAllMocks();
  });

  afterEach(() => {
    jest.resetAllMocks();
  });

  it('should track an ApplicationLoadedEvent (automatically by ObjectivProvider)', () => {
    const tracker = new Tracker({ applicationId: 'app-id' });
    jest.spyOn(tracker, 'trackEvent');

    const { rerender } = render(<ObjectivProvider tracker={tracker}>app</ObjectivProvider>);

    rerender(<ObjectivProvider tracker={tracker}>app</ObjectivProvider>);

    expect(tracker.trackEvent).toHaveBeenCalledTimes(1);
    expect(tracker.trackEvent).toHaveBeenNthCalledWith(
      1,
      expect.objectContaining(makeApplicationLoadedEvent()),
      undefined
    );
  });

  it('should track an ApplicationLoadedEvent (programmatic)', () => {
    const tracker = new Tracker({ applicationId: 'app-id' });
    jest.spyOn(tracker, 'trackEvent');

    trackApplicationLoadedEvent({ tracker });

    expect(tracker.trackEvent).toHaveBeenCalledTimes(1);
    expect(tracker.trackEvent).toHaveBeenNthCalledWith(
      1,
      expect.objectContaining(makeApplicationLoadedEvent()),
      undefined
    );
  });

  it('should track an ApplicationLoadedEvent (hook relying on TrackingContextProvider)', () => {
    const spyTransport = { transportName: 'SpyTransport', handle: jest.fn(), isUsable: () => true };
    const tracker = new Tracker({ applicationId: 'app-id', transport: spyTransport });

    const Component = () => {
      const trackApplicationLoadedEvent = useApplicationLoadedEventTracker();
      trackApplicationLoadedEvent();

      return <>Component triggering ApplicationLoadedEvent</>;
    };

    render(
      <TrackingContextProvider tracker={tracker}>
        <Component />
      </TrackingContextProvider>
    );

    expect(spyTransport.handle).toHaveBeenCalledTimes(1);
    expect(spyTransport.handle).toHaveBeenNthCalledWith(
      1,
      expect.objectContaining({ _type: 'ApplicationLoadedEvent' })
    );
  });

  it('should track an ApplicationLoadedEvent (hook with custom tracker and location)', () => {
    const tracker = new Tracker({ applicationId: 'app-id' });
    jest.spyOn(tracker, 'trackEvent');

    const customTracker = new Tracker({ applicationId: 'app-id-2' });
    jest.spyOn(customTracker, 'trackEvent');

    const Component = () => {
      const trackApplicationLoadedEvent = useApplicationLoadedEventTracker({
        tracker: customTracker,
        locationStack: [makeSectionContext({ id: 'override' })],
      });
      trackApplicationLoadedEvent();

      return <>Component triggering ApplicationLoadedEvent</>;
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
        makeApplicationLoadedEvent({
          location_stack: [expect.objectContaining({ _type: 'SectionContext', id: 'override' })],
        })
      ),
      undefined
    );
  });
});
