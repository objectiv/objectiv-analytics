/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { ApplicationContextPlugin } from '@objectiv/plugin-application-context';
import {
  EventName,
  GlobalContextName,
  LocationContextName,
  makeApplicationLoadedEvent,
  makeContentContext,
  makeInputValueContext,
  Tracker,
} from '@objectiv/tracker-core';
import { render } from '@testing-library/react';
import React from 'react';
import {
  ContentContextWrapper,
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
    const LogTransport = { transportName: 'LogTransport', handle: jest.fn(), isUsable: () => true };
    const tracker = new Tracker({ applicationId: 'app-id', transport: LogTransport });

    const Component = () => {
      const trackApplicationLoadedEvent = useApplicationLoadedEventTracker({ globalContexts: [] });
      trackApplicationLoadedEvent();

      return <>Component triggering ApplicationLoadedEvent</>;
    };

    render(
      <TrackingContextProvider tracker={tracker}>
        <Component />
      </TrackingContextProvider>
    );

    expect(LogTransport.handle).toHaveBeenCalledTimes(1);
    expect(LogTransport.handle).toHaveBeenNthCalledWith(
      1,
      expect.objectContaining({ _type: 'ApplicationLoadedEvent' })
    );
  });

  it('should track an ApplicationLoadedEvent (hook with a custom location stack)', () => {
    const LogTransport = { transportName: 'LogTransport', handle: jest.fn(), isUsable: () => true };
    const tracker = new Tracker({ applicationId: 'app-id', transport: LogTransport });

    const Component = () => {
      const trackApplicationLoadedEvent = useApplicationLoadedEventTracker();
      trackApplicationLoadedEvent({
        locationStack: [makeContentContext({ id: 'extra' })],
      });

      return <>Component triggering ApplicationLoadedEvent</>;
    };

    render(
      <TrackingContextProvider tracker={tracker}>
        <ContentContextWrapper id={'wrapper'}>
          <Component />
        </ContentContextWrapper>
      </TrackingContextProvider>
    );

    expect(LogTransport.handle).toHaveBeenCalledTimes(1);
    expect(LogTransport.handle).toHaveBeenNthCalledWith(
      1,
      expect.objectContaining({
        _type: EventName.ApplicationLoadedEvent,
        location_stack: [
          expect.objectContaining({
            _type: LocationContextName.ContentContext,
            id: 'wrapper',
          }),
          expect.objectContaining({
            _type: LocationContextName.ContentContext,
            id: 'extra',
          }),
        ],
      })
    );
  });

  it('should track an ApplicationLoadedEvent (hook with custom global context)', () => {
    const LogTransport = { transportName: 'LogTransport', handle: jest.fn(), isUsable: () => true };
    const tracker = new Tracker({
      applicationId: 'app-id',
      transport: LogTransport,
      plugins: [new ApplicationContextPlugin()],
    });

    const Component = () => {
      const trackApplicationLoadedEvent = useApplicationLoadedEventTracker();
      trackApplicationLoadedEvent({
        globalContexts: [
          makeInputValueContext({
            id: 'test',
            value: 'test-value',
          }),
        ],
      });

      return <>Component triggering ApplicationLoadedEvent</>;
    };

    render(
      <TrackingContextProvider tracker={tracker}>
        <ContentContextWrapper id={'wrapper'}>
          <Component />
        </ContentContextWrapper>
      </TrackingContextProvider>
    );

    expect(LogTransport.handle).toHaveBeenCalledTimes(1);
    expect(LogTransport.handle).toHaveBeenNthCalledWith(
      1,
      expect.objectContaining({
        _type: EventName.ApplicationLoadedEvent,
        global_contexts: [
          expect.objectContaining({
            _type: GlobalContextName.InputValueContext,
            id: 'test',
            value: 'test-value',
          }),
          expect.objectContaining({ _type: GlobalContextName.ApplicationContext }),
        ],
      })
    );
  });

  it('should track an ApplicationLoadedEvent (hook with custom options)', () => {
    const LogTransport = { transportName: 'LogTransport', handle: jest.fn(), isUsable: () => true };
    const tracker = new Tracker({
      applicationId: 'app-id',
      transport: LogTransport,
      plugins: [new ApplicationContextPlugin()],
    });

    const Component = () => {
      const trackApplicationLoadedEvent = useApplicationLoadedEventTracker();
      trackApplicationLoadedEvent({
        options: {
          waitForQueue: true,
        },
      });

      return <>Component triggering ApplicationLoadedEvent</>;
    };

    render(
      <TrackingContextProvider tracker={tracker}>
        <Component />
      </TrackingContextProvider>
    );

    expect(LogTransport.handle).toHaveBeenCalledTimes(1);
    expect(LogTransport.handle).toHaveBeenNthCalledWith(
      1,
      expect.objectContaining({ _type: EventName.ApplicationLoadedEvent })
    );
  });

  it('should track an ApplicationLoadedEvent (hook with custom options at construction)', () => {
    const LogTransport = { transportName: 'LogTransport', handle: jest.fn(), isUsable: () => true };
    const tracker = new Tracker({
      applicationId: 'app-id',
      transport: LogTransport,
      plugins: [new ApplicationContextPlugin()],
    });

    const Component = () => {
      const trackApplicationLoadedEvent = useApplicationLoadedEventTracker({ options: { waitForQueue: true } });
      trackApplicationLoadedEvent();

      return <>Component triggering ApplicationLoadedEvent</>;
    };

    render(
      <TrackingContextProvider tracker={tracker}>
        <Component />
      </TrackingContextProvider>
    );

    expect(LogTransport.handle).toHaveBeenCalledTimes(1);
    expect(LogTransport.handle).toHaveBeenNthCalledWith(
      1,
      expect.objectContaining({ _type: EventName.ApplicationLoadedEvent })
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
        locationStack: [makeContentContext({ id: 'override' })],
      });
      trackApplicationLoadedEvent();

      return <>Component triggering ApplicationLoadedEvent</>;
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
        makeApplicationLoadedEvent({
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
