/*
 * Copyright 2022 Objectiv B.V.
 */

import { MockConsoleImplementation, SpyTransport } from '@objectiv/testing-tools';
import { LocationContextName } from '@objectiv/tracker-core';
import { fireEvent, getByText, render, screen } from '@testing-library/react';
import React, { createRef } from 'react';
import { ObjectivProvider, ReactTracker, TrackedOverlayContext, usePressEventTracker } from '../src';

require('@objectiv/developer-tools');
globalThis.objectiv?.TrackerConsole.setImplementation(MockConsoleImplementation);

const TrackedButton = () => {
  const trackPressEvent = usePressEventTracker();
  return <div onClick={trackPressEvent}>Trigger Event</div>;
};

describe('TrackedOverlayContext', () => {
  beforeEach(() => {
    jest.resetAllMocks();
  });

  afterEach(() => {
    jest.resetAllMocks();
  });

  it('should wrap the given Component in an OverlayContext', () => {
    const spyTransport = new SpyTransport();
    jest.spyOn(spyTransport, 'handle');
    const tracker = new ReactTracker({ applicationId: 'app-id', transport: spyTransport });

    const { container } = render(
      <ObjectivProvider tracker={tracker}>
        <TrackedOverlayContext Component={'div'} id={'modal-id'}>
          <TrackedButton />
        </TrackedOverlayContext>
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
            _type: LocationContextName.OverlayContext,
            id: 'modal-id',
          }),
        ]),
      })
    );
  });

  it('should not track an HiddenEvent when initialized with isVisible=false', () => {
    const spyTransport = new SpyTransport();
    jest.spyOn(spyTransport, 'handle');
    const tracker = new ReactTracker({ applicationId: 'app-id', transport: spyTransport });

    render(
      <ObjectivProvider tracker={tracker}>
        <TrackedOverlayContext Component={'div'} id={'modal-id'} isVisible={false}>
          <TrackedButton />
        </TrackedOverlayContext>
      </ObjectivProvider>
    );

    expect(spyTransport.handle).not.toHaveBeenCalledWith(
      expect.objectContaining({
        _type: 'HiddenEvent',
      })
    );
  });

  it('should track an VisibleEvent when isVisible switches from false to true and vice-versa a HiddenEvent', () => {
    const spyTransport = new SpyTransport();
    jest.spyOn(spyTransport, 'handle');
    const tracker = new ReactTracker({ applicationId: 'app-id', transport: spyTransport });

    const { rerender } = render(
      <ObjectivProvider tracker={tracker}>
        <TrackedOverlayContext Component={'div'} id={'modal-id'} isVisible={false}>
          <TrackedButton />
        </TrackedOverlayContext>
      </ObjectivProvider>
    );

    expect(spyTransport.handle).not.toHaveBeenCalledWith(
      expect.objectContaining({
        _type: 'HiddenEvent',
      })
    );

    jest.resetAllMocks();

    rerender(
      <ObjectivProvider tracker={tracker}>
        <TrackedOverlayContext Component={'div'} id={'modal-id'} isVisible={true}>
          <TrackedButton />
        </TrackedOverlayContext>
      </ObjectivProvider>
    );

    expect(spyTransport.handle).toHaveBeenCalledTimes(1);
    expect(spyTransport.handle).toHaveBeenCalledWith(
      expect.objectContaining({
        _type: 'VisibleEvent',
      })
    );

    jest.resetAllMocks();

    rerender(
      <ObjectivProvider tracker={tracker}>
        <TrackedOverlayContext Component={'div'} id={'modal-id'} isVisible={false}>
          <TrackedButton />
        </TrackedOverlayContext>
      </ObjectivProvider>
    );

    expect(spyTransport.handle).toHaveBeenCalledTimes(1);
    expect(spyTransport.handle).toHaveBeenCalledWith(
      expect.objectContaining({
        _type: 'HiddenEvent',
      })
    );
  });

  it('should allow forwarding the id property', () => {
    const tracker = new ReactTracker({ applicationId: 'app-id', transport: new SpyTransport() });

    render(
      <ObjectivProvider tracker={tracker}>
        <TrackedOverlayContext Component={'div'} id={'modal-id-1'} data-testid={'test-overlay-1'}>
          test
        </TrackedOverlayContext>
        <TrackedOverlayContext Component={'div'} id={'modal-id-2'} forwardId={true} data-testid={'test-overlay-2'}>
          test
        </TrackedOverlayContext>
      </ObjectivProvider>
    );

    expect(screen.getByTestId('test-overlay-1').getAttribute('id')).toBe(null);
    expect(screen.getByTestId('test-overlay-2').getAttribute('id')).toBe('modal-id-2');
  });

  it('should allow forwarding refs', () => {
    const tracker = new ReactTracker({ applicationId: 'app-id', transport: new SpyTransport() });
    const ref = createRef<HTMLDivElement>();

    render(
      <ObjectivProvider tracker={tracker}>
        <TrackedOverlayContext Component={'div'} id={'modal-id'} ref={ref}>
          Modal content
        </TrackedOverlayContext>
      </ObjectivProvider>
    );

    expect(ref.current).toMatchInlineSnapshot(`
      <div>
        Modal content
      </div>
    `);
  });
});
