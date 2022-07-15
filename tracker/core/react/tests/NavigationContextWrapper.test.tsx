/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { LocationContextName, Tracker } from '@objectiv/tracker-core';
import { fireEvent, getByText, render } from '@testing-library/react';
import React from 'react';
import { NavigationContextWrapper, ObjectivProvider, trackPressEvent, usePressEventTracker } from '../src';

describe('NavigationContextWrapper', () => {
  beforeEach(() => {
    jest.resetAllMocks();
  });

  afterEach(() => {
    jest.resetAllMocks();
  });

  it('should wrap the given children in a NavigationContext (trigger via Component)', () => {
    const LogTransport = { transportName: 'LogTransport', handle: jest.fn(), isUsable: () => true };
    const tracker = new Tracker({ applicationId: 'app-id', transport: LogTransport });
    jest.spyOn(LogTransport, 'handle');

    const navigationContextProps = { id: 'test-navigation' };
    const TrackedButton = () => {
      const trackPressEvent = usePressEventTracker();
      return <nav onClick={() => trackPressEvent()}>Trigger Event</nav>;
    };
    const { container } = render(
      <ObjectivProvider tracker={tracker}>
        <NavigationContextWrapper {...navigationContextProps}>
          <TrackedButton />
        </NavigationContextWrapper>
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
            _type: LocationContextName.NavigationContext,
            ...navigationContextProps,
          }),
        ],
      })
    );
  });

  it('should wrap the given children in a NavigationContext (trigger via render-props)', () => {
    const LogTransport = { transportName: 'LogTransport', handle: jest.fn(), isUsable: () => true };
    const tracker = new Tracker({ applicationId: 'app-id', transport: LogTransport });
    jest.spyOn(LogTransport, 'handle');

    const navigationContextProps = { id: 'test-navigation' };
    const { container } = render(
      <ObjectivProvider tracker={tracker}>
        <NavigationContextWrapper {...navigationContextProps}>
          {(trackingContext) => <nav onClick={() => trackPressEvent(trackingContext)}>Trigger Event</nav>}
        </NavigationContextWrapper>
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
            _type: LocationContextName.NavigationContext,
            ...navigationContextProps,
          }),
        ],
      })
    );
  });
});
