/*
 * Copyright 2022 Objectiv B.V.
 */

import { MockConsoleImplementation, SpyTransport } from '@objectiv/testing-tools';
import { LocationContextName } from '@objectiv/tracker-core';
import { fireEvent, getByText, render, screen } from '@testing-library/react';
import React, { createRef } from 'react';
import { ObjectivProvider, ReactTracker, TrackedMediaPlayerContext, usePressEventTracker } from '../src';

require('@objectiv/developer-tools');
globalThis.objectiv?.TrackerConsole.setImplementation(MockConsoleImplementation);

describe('TrackedMediaPlayerContext', () => {
  beforeEach(() => {
    jest.resetAllMocks();
  });

  afterEach(() => {
    jest.resetAllMocks();
  });

  it('should wrap the given Component in a MediaPlayerContext', () => {
    const spyTransport = new SpyTransport();
    jest.spyOn(spyTransport, 'handle');
    const tracker = new ReactTracker({ applicationId: 'app-id', transport: spyTransport });

    const TrackedButton = () => {
      const trackPressEvent = usePressEventTracker();
      return <video onClick={trackPressEvent}>Trigger Event</video>;
    };

    const { container } = render(
      <ObjectivProvider tracker={tracker}>
        <TrackedMediaPlayerContext Component={'video'} id={'video-id'}>
          <TrackedButton />
        </TrackedMediaPlayerContext>
      </ObjectivProvider>
    );

    fireEvent.click(getByText(container, /trigger event/i));

    expect(spyTransport.handle).toHaveBeenCalledTimes(2);
    expect(spyTransport.handle).toHaveBeenNthCalledWith(
      1,
      expect.objectContaining({
        _type: 'ApplicationLoadedEvent',
      })
    );
    expect(spyTransport.handle).toHaveBeenNthCalledWith(
      2,
      expect.objectContaining({
        _type: 'PressEvent',
        location_stack: expect.arrayContaining([
          expect.objectContaining({
            _type: LocationContextName.MediaPlayerContext,
            id: 'video-id',
          }),
        ]),
      })
    );
  });

  it('should allow forwarding the id property', () => {
    const tracker = new ReactTracker({ applicationId: 'app-id', transport: new SpyTransport() });

    render(
      <ObjectivProvider tracker={tracker}>
        <TrackedMediaPlayerContext Component={'video'} id={'video-id-1'} data-testid={'test-video-1'}>
          test
        </TrackedMediaPlayerContext>
        <TrackedMediaPlayerContext Component={'video'} id={'video-id-2'} forwardId={true} data-testid={'test-video-2'}>
          test
        </TrackedMediaPlayerContext>
      </ObjectivProvider>
    );

    expect(screen.getByTestId('test-video-1').getAttribute('id')).toBe(null);
    expect(screen.getByTestId('test-video-2').getAttribute('id')).toBe('video-id-2');
  });

  it('should allow forwarding refs', () => {
    const tracker = new ReactTracker({ applicationId: 'app-id', transport: new SpyTransport() });
    const ref = createRef<HTMLDivElement>();

    render(
      <ObjectivProvider tracker={tracker}>
        <TrackedMediaPlayerContext Component={'video'} id={'video-id'} ref={ref}>
          test
        </TrackedMediaPlayerContext>
      </ObjectivProvider>
    );

    expect(ref.current).toMatchInlineSnapshot(`
      <video>
        test
      </video>
    `);
  });
});
