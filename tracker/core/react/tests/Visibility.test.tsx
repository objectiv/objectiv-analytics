/*
 * Copyright 2021 Objectiv B.V.
 */

import { makeSectionHiddenEvent, makeSectionVisibleEvent, Tracker } from '@objectiv/tracker-core';
import { render } from '@testing-library/react';
import { makeSectionContext, TrackingContextProvider, trackVisibility, useVisibilityTracker } from '../src';

describe('Visibility', () => {
  beforeEach(() => {
    jest.resetAllMocks();
  });

  afterEach(() => {
    jest.resetAllMocks();
  });

  it('should track a SectionHiddenEvent (programmatic)', () => {
    const tracker = new Tracker({ applicationId: 'app-id' });
    jest.spyOn(tracker, 'trackEvent');

    trackVisibility({ tracker, isVisible: false });

    expect(tracker.trackEvent).toHaveBeenCalledTimes(1);
    expect(tracker.trackEvent).toHaveBeenNthCalledWith(1, expect.objectContaining(makeSectionHiddenEvent()), undefined);
  });

  it('should track a SectionHiddenEvent (hook relying on TrackingContextProvider)', () => {
    const spyTransport = { transportName: 'SpyTransport', handle: jest.fn(), isUsable: () => true };
    const tracker = new Tracker({ applicationId: 'app-id', transport: spyTransport });

    const Component = () => {
      const trackVisibility = useVisibilityTracker({ isVisible: false });
      trackVisibility();

      return <>Component triggering SectionHiddenEvent via Visibility Event Tracker</>;
    };

    render(
      <TrackingContextProvider tracker={tracker}>
        <Component />
      </TrackingContextProvider>
    );

    expect(spyTransport.handle).toHaveBeenCalledTimes(1);
    expect(spyTransport.handle).toHaveBeenNthCalledWith(1, expect.objectContaining({ _type: 'SectionHiddenEvent' }));
  });

  it('should track a SectionHiddenEvent (hook with custom tracker and location)', () => {
    const tracker = new Tracker({ applicationId: 'app-id' });
    jest.spyOn(tracker, 'trackEvent');

    const customTracker = new Tracker({ applicationId: 'app-id-2' });
    jest.spyOn(customTracker, 'trackEvent');

    const Component = () => {
      const trackVisibility = useVisibilityTracker({
        isVisible: false,
        tracker: customTracker,
        locationStack: [makeSectionContext({ id: 'override' })],
      });
      trackVisibility();

      return <>Component triggering SectionHiddenEvent</>;
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
        makeSectionHiddenEvent({
          location_stack: [expect.objectContaining({ _type: 'SectionContext', id: 'override' })],
        })
      ),
      undefined
    );
  });

  it('should track a SectionVisibleEvent (programmatic)', () => {
    const tracker = new Tracker({ applicationId: 'app-id' });
    jest.spyOn(tracker, 'trackEvent');

    trackVisibility({ tracker, isVisible: true });

    expect(tracker.trackEvent).toHaveBeenCalledTimes(1);
    expect(tracker.trackEvent).toHaveBeenNthCalledWith(
      1,
      expect.objectContaining(makeSectionVisibleEvent()),
      undefined
    );
  });

  it('should track a SectionVisibleEvent (hook relying on TrackingContextProvider)', () => {
    const spyTransport = { transportName: 'SpyTransport', handle: jest.fn(), isUsable: () => true };
    const tracker = new Tracker({ applicationId: 'app-id', transport: spyTransport });

    const Component = () => {
      const trackVisibility = useVisibilityTracker({ isVisible: true });
      trackVisibility();

      return <>Component triggering SectionVisibleEvent via Visibility Event Tracker</>;
    };

    render(
      <TrackingContextProvider tracker={tracker}>
        <Component />
      </TrackingContextProvider>
    );

    expect(spyTransport.handle).toHaveBeenCalledTimes(1);
    expect(spyTransport.handle).toHaveBeenNthCalledWith(1, expect.objectContaining({ _type: 'SectionVisibleEvent' }));
  });

  it('should track a SectionVisibleEvent (hook with custom tracker and location)', () => {
    const tracker = new Tracker({ applicationId: 'app-id' });
    jest.spyOn(tracker, 'trackEvent');

    const customTracker = new Tracker({ applicationId: 'app-id-2' });
    jest.spyOn(customTracker, 'trackEvent');

    const Component = () => {
      const trackVisibility = useVisibilityTracker({
        isVisible: true,
        tracker: customTracker,
        locationStack: [makeSectionContext({ id: 'override' })],
      });
      trackVisibility();

      return <>Component triggering SectionVisibleEvent via Visibility Event Tracker</>;
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
        makeSectionVisibleEvent({
          location_stack: [expect.objectContaining({ _type: 'SectionContext', id: 'override' })],
        })
      ),
      undefined
    );
  });
});
