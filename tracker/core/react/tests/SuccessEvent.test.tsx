/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { ApplicationContextPlugin } from '@objectiv/plugin-application-context';
import { PathContextFromURLPlugin } from '@objectiv/plugin-path-context-from-url';
import {
  EventName,
  GlobalContextName,
  LocationContextName,
  makeContentContext,
  makeInputValueContext,
  makeRootLocationContext,
  makeSuccessEvent,
  Tracker,
} from '@objectiv/tracker-core';
import { render } from '@testing-library/react';
import React from 'react';
import { ContentContextWrapper, TrackingContextProvider, trackSuccessEvent, useSuccessEventTracker } from '../src';

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
    const LogTransport = { transportName: 'LogTransport', handle: jest.fn(), isUsable: () => true };
    const tracker = new Tracker({ applicationId: 'app-id', transport: LogTransport });

    const Component = () => {
      const trackSuccessEvent = useSuccessEventTracker({ globalContexts: [] });
      trackSuccessEvent({ message: 'ok' });

      return <>Component triggering SuccessEvent</>;
    };

    render(
      <TrackingContextProvider tracker={tracker}>
        <Component />
      </TrackingContextProvider>
    );

    expect(LogTransport.handle).toHaveBeenCalledTimes(1);
    expect(LogTransport.handle).toHaveBeenNthCalledWith(1, expect.objectContaining({ _type: 'SuccessEvent' }));
  });

  it('should track a SuccessEvent (hook with custom location stack)', () => {
    const LogTransport = { transportName: 'LogTransport', handle: jest.fn(), isUsable: () => true };
    const tracker = new Tracker({ applicationId: 'app-id', transport: LogTransport });

    const Component = () => {
      const trackSuccessEvent = useSuccessEventTracker();
      trackSuccessEvent({
        message: 'ok',
        locationStack: [makeContentContext({ id: 'extra' })],
      });

      return <>Component triggering SuccessEvent</>;
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
        _type: EventName.SuccessEvent,
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

  it('should track a SuccessEvent (hook with custom global context)', () => {
    const LogTransport = { transportName: 'LogTransport', handle: jest.fn(), isUsable: () => true };
    const tracker = new Tracker({
      applicationId: 'app-id',
      transport: LogTransport,
      plugins: [new ApplicationContextPlugin()],
    });

    const Component = () => {
      const trackSuccessEvent = useSuccessEventTracker();
      trackSuccessEvent({
        message: 'ok',
        globalContexts: [
          makeInputValueContext({
            id: 'test',
            value: 'test-value',
          }),
        ],
      });

      return <>Component triggering SuccessEvent</>;
    };

    render(
      <TrackingContextProvider tracker={tracker}>
        <Component />
      </TrackingContextProvider>
    );

    expect(LogTransport.handle).toHaveBeenCalledTimes(1);
    expect(LogTransport.handle).toHaveBeenNthCalledWith(
      1,
      expect.objectContaining({
        _type: EventName.SuccessEvent,
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

  it('should track a SuccessEvent (hook with custom options)', () => {
    const LogTransport = { transportName: 'LogTransport', handle: jest.fn(), isUsable: () => true };
    const tracker = new Tracker({
      applicationId: 'app-id',
      transport: LogTransport,
      plugins: [new ApplicationContextPlugin()],
    });

    const Component = () => {
      const trackSuccessEvent = useSuccessEventTracker();
      trackSuccessEvent({
        message: 'ok',
        options: {
          waitForQueue: true,
        },
      });

      return <>Component triggering SuccessEvent</>;
    };

    render(
      <TrackingContextProvider tracker={tracker}>
        <Component />
      </TrackingContextProvider>
    );

    expect(LogTransport.handle).toHaveBeenCalledTimes(1);
    expect(LogTransport.handle).toHaveBeenNthCalledWith(1, expect.objectContaining({ _type: EventName.SuccessEvent }));
  });

  it('should track a SuccessEvent (hook with custom options at construction)', () => {
    const LogTransport = { transportName: 'LogTransport', handle: jest.fn(), isUsable: () => true };
    const tracker = new Tracker({
      applicationId: 'app-id',
      transport: LogTransport,
      plugins: [new ApplicationContextPlugin()],
    });

    const Component = () => {
      const trackSuccessEvent = useSuccessEventTracker({ options: { waitForQueue: true } });
      trackSuccessEvent({
        message: 'ok',
      });

      return <>Component triggering SuccessEvent</>;
    };

    render(
      <TrackingContextProvider tracker={tracker}>
        <Component />
      </TrackingContextProvider>
    );

    expect(LogTransport.handle).toHaveBeenCalledTimes(1);
    expect(LogTransport.handle).toHaveBeenNthCalledWith(1, expect.objectContaining({ _type: EventName.SuccessEvent }));
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

  it('should track a SuccessEvent (hook with both its options and more options in the callback)', () => {
    const LogTransport = { transportName: 'LogTransport', handle: jest.fn(), isUsable: () => true };
    const tracker = new Tracker({
      applicationId: 'app-id',
      transport: LogTransport,
      plugins: [new ApplicationContextPlugin(), new PathContextFromURLPlugin()],
      location_stack: [makeRootLocationContext({ id: 'root' })],
    });

    const Component = () => {
      const trackSuccessEvent = useSuccessEventTracker({
        locationStack: [
          makeContentContext({ id: 'virtual-content-location-1' }),
          makeContentContext({ id: 'virtual-content-location-2' }),
        ],
        globalContexts: [
          makeInputValueContext({ id: 'test-input-value-1', value: 'a' }),
          makeInputValueContext({ id: 'test-input-value-2', value: 'b' }),
        ],
      });
      trackSuccessEvent({
        message: 'ok',
        locationStack: [
          makeContentContext({ id: 'virtual-content-location-3' }),
          makeContentContext({ id: 'virtual-content-location-4' }),
        ],
        globalContexts: [
          makeInputValueContext({ id: 'test-input-value-3', value: 'c' }),
          makeInputValueContext({ id: 'test-input-value-4', value: 'd' }),
        ],
      });

      return <>Component triggering SuccessEvent</>;
    };

    render(
      <TrackingContextProvider tracker={tracker}>
        <Component />
      </TrackingContextProvider>
    );

    expect(LogTransport.handle).toHaveBeenCalledTimes(1);
    expect(LogTransport.handle).toHaveBeenNthCalledWith(
      1,
      expect.objectContaining({
        _type: EventName.SuccessEvent,
        global_contexts: [
          expect.objectContaining({ _type: GlobalContextName.InputValueContext, id: 'test-input-value-1', value: 'a' }),
          expect.objectContaining({ _type: GlobalContextName.InputValueContext, id: 'test-input-value-2', value: 'b' }),
          expect.objectContaining({ _type: GlobalContextName.InputValueContext, id: 'test-input-value-3', value: 'c' }),
          expect.objectContaining({ _type: GlobalContextName.InputValueContext, id: 'test-input-value-4', value: 'd' }),
          expect.objectContaining({ _type: GlobalContextName.ApplicationContext }),
          expect.objectContaining({ _type: GlobalContextName.PathContext }),
        ],
        location_stack: [
          expect.objectContaining({ _type: LocationContextName.RootLocationContext, id: 'root' }),
          expect.objectContaining({ _type: LocationContextName.ContentContext, id: 'virtual-content-location-1' }),
          expect.objectContaining({ _type: LocationContextName.ContentContext, id: 'virtual-content-location-2' }),
          expect.objectContaining({ _type: LocationContextName.ContentContext, id: 'virtual-content-location-3' }),
          expect.objectContaining({ _type: LocationContextName.ContentContext, id: 'virtual-content-location-4' }),
        ],
      })
    );
  });
});
