/*
 * Copyright 2021 Objectiv B.V.
 */

import { Tracker } from '@objectiv/tracker-core';
import { fireEvent, getByText, render } from '@testing-library/react';
import { OverlayContextWrapper, ObjectivProvider, trackClickEvent, useClickEventTracker, LocationTree } from '../src';

describe('OverlayContextWrapper', () => {
  beforeEach(() => {
    jest.resetAllMocks();
    LocationTree.clear();
  });

  afterEach(() => {
    jest.resetAllMocks();
  });

  it('should wrap the given children in a OverlayContext (trigger via Component)', () => {
    const spyTransport = { transportName: 'SpyTransport', handle: jest.fn(), isUsable: () => true };
    const tracker = new Tracker({ applicationId: 'app-id', transport: spyTransport });
    jest.spyOn(spyTransport, 'handle');

    const overlayContextProps = { id: 'test-overlay' };
    const TrackedButton = () => {
      const trackClickEvent = useClickEventTracker();
      return <div onClick={trackClickEvent}>Trigger Event</div>;
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

    expect(spyTransport.handle).toHaveBeenCalledTimes(1);
    expect(spyTransport.handle).toHaveBeenNthCalledWith(
      1,
      expect.objectContaining({
        _type: 'ClickEvent',
        location_stack: [
          expect.objectContaining({
            _type: 'OverlayContext',
            ...overlayContextProps,
          }),
        ],
      })
    );
  });

  it('should wrap the given children in a OverlayContext (trigger via render-props)', () => {
    const spyTransport = { transportName: 'SpyTransport', handle: jest.fn(), isUsable: () => true };
    const tracker = new Tracker({ applicationId: 'app-id', transport: spyTransport });
    jest.spyOn(spyTransport, 'handle');

    const overlayContextProps = { id: 'test-overlay' };
    const { container } = render(
      <ObjectivProvider tracker={tracker}>
        <OverlayContextWrapper {...overlayContextProps}>
          {(trackingContext) => <div onClick={() => trackClickEvent(trackingContext)}>Trigger Event</div>}
        </OverlayContextWrapper>
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
            _type: 'OverlayContext',
            ...overlayContextProps,
          }),
        ],
      })
    );
  });
});
