/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { LocationContextName, Tracker } from '@objectiv/tracker-core';
import { fireEvent, getByText, render } from '@testing-library/react';
import React from 'react';
import { ObjectivProvider, OverlayContextWrapper, trackPressEvent, usePressEventTracker } from '../src';

describe('OverlayContextWrapper', () => {
  beforeEach(() => {
    jest.resetAllMocks();
  });

  afterEach(() => {
    jest.resetAllMocks();
  });

  it('should wrap the given children in a OverlayContext (trigger via Component)', () => {
    const LogTransport = { transportName: 'LogTransport', handle: jest.fn(), isUsable: () => true };
    const tracker = new Tracker({ applicationId: 'app-id', transport: LogTransport });
    jest.spyOn(LogTransport, 'handle');

    const overlayContextProps = { id: 'test-overlay' };
    const TrackedButton = () => {
      const trackPressEvent = usePressEventTracker();
      return <div onClick={() => trackPressEvent()}>Trigger Event</div>;
    };
    const { container } = render(
      <ObjectivProvider tracker={tracker}>
        <OverlayContextWrapper {...overlayContextProps}>
          <TrackedButton />
        </OverlayContextWrapper>
      </ObjectivProvider>
    );

    jest.resetAllMocks();

    fireEvent.click(getByText(container, /trigger event/i));

    expect(LogTransport.handle).toHaveBeenCalledTimes(1);
    expect(LogTransport.handle).toHaveBeenNthCalledWith(
      1,
      expect.objectContaining({
        _type: 'PressEvent',
        location_stack: [
          expect.objectContaining({
            _type: LocationContextName.OverlayContext,
            ...overlayContextProps,
          }),
        ],
      })
    );
  });

  it('should wrap the given children in a OverlayContext (trigger via render-props)', () => {
    const LogTransport = { transportName: 'LogTransport', handle: jest.fn(), isUsable: () => true };
    const tracker = new Tracker({ applicationId: 'app-id', transport: LogTransport });
    jest.spyOn(LogTransport, 'handle');

    const overlayContextProps = { id: 'test-overlay' };
    const { container } = render(
      <ObjectivProvider tracker={tracker}>
        <OverlayContextWrapper {...overlayContextProps}>
          {(trackingContext) => <div onClick={() => trackPressEvent(trackingContext)}>Trigger Event</div>}
        </OverlayContextWrapper>
      </ObjectivProvider>
    );

    jest.resetAllMocks();

    fireEvent.click(getByText(container, /trigger event/i));

    expect(LogTransport.handle).toHaveBeenCalledTimes(1);
    expect(LogTransport.handle).toHaveBeenNthCalledWith(
      1,
      expect.objectContaining({
        _type: 'PressEvent',
        location_stack: [
          expect.objectContaining({
            _type: LocationContextName.OverlayContext,
            ...overlayContextProps,
          }),
        ],
      })
    );
  });
});
