/*
 * Copyright 2021 Objectiv B.V.
 */

import { Tracker } from '@objectiv/tracker-core';
import { fireEvent, getByText, render } from '@testing-library/react';
import {
  LocationTree,
  NavigationContextWrapper,
  ObjectivProvider,
  trackClickEvent,
  useClickEventTracker,
} from '../src';

describe('NavigationContextWrapper', () => {
  beforeEach(() => {
    jest.resetAllMocks();
    LocationTree.clear();
  });

  afterEach(() => {
    jest.resetAllMocks();
  });

  it('should wrap the given children in a NavigationContext (trigger via Component)', () => {
    const spyTransport = { transportName: 'SpyTransport', handle: jest.fn(), isUsable: () => true };
    const tracker = new Tracker({ applicationId: 'app-id', transport: spyTransport });
    jest.spyOn(spyTransport, 'handle');

    const navigationContextProps = { id: 'test-navigation' };
    const TrackedButton = () => {
      const trackClickEvent = useClickEventTracker();
      return <nav onClick={trackClickEvent}>Trigger Event</nav>;
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

    expect(spyTransport.handle).toHaveBeenCalledTimes(1);
    expect(spyTransport.handle).toHaveBeenNthCalledWith(
      1,
      expect.objectContaining({
        _type: 'ClickEvent',
        location_stack: [
          expect.objectContaining({
            _type: 'NavigationContext',
            ...navigationContextProps,
          }),
        ],
      })
    );
  });

  it('should wrap the given children in a NavigationContext (trigger via render-props)', () => {
    const spyTransport = { transportName: 'SpyTransport', handle: jest.fn(), isUsable: () => true };
    const tracker = new Tracker({ applicationId: 'app-id', transport: spyTransport });
    jest.spyOn(spyTransport, 'handle');

    const navigationContextProps = { id: 'test-navigation' };
    const { container } = render(
      <ObjectivProvider tracker={tracker}>
        <NavigationContextWrapper {...navigationContextProps}>
          {(trackingContext) => <nav onClick={() => trackClickEvent(trackingContext)}>Trigger Event</nav>}
        </NavigationContextWrapper>
      </ObjectivProvider>
    );

    jest.resetAllMocks();

    fireEvent.click(getByText(container, /trigger event/i));

    expect(spyTransport.handle).toHaveBeenCalledTimes(1);
    expect(spyTransport.handle).toHaveBeenNthCalledWith(
      1,
      expect.objectContaining({
        _type: 'ClickEvent',
        location_stack: [
          expect.objectContaining({
            _type: 'NavigationContext',
            ...navigationContextProps,
          }),
        ],
      })
    );
  });
});
