/*
 * Copyright 2021 Objectiv B.V.
 */

import { Tracker } from '@objectiv/tracker-core';
import { fireEvent, getByTestId, render } from '@testing-library/react';
import { ItemContextWrapper, LocationTree, ObjectivProvider, trackClickEvent, useClickEventTracker } from '../src';

describe('ItemContextWrapper', () => {
  beforeEach(() => {
    jest.resetAllMocks();
    LocationTree.clear();
  });

  afterEach(() => {
    jest.resetAllMocks();
  });

  it('should wrap the given children in a ItemContext (trigger via Component)', () => {
    const spyTransport = { transportName: 'SpyTransport', handle: jest.fn(), isUsable: () => true };
    const tracker = new Tracker({ applicationId: 'app-id', transport: spyTransport });
    jest.spyOn(spyTransport, 'handle');

    const itemContextProps = { id: 'test-item' };
    const TrackedIcon = () => {
      const trackClickEvent = useClickEventTracker();
      return <img onClick={trackClickEvent} data-testid={'img'} alt={'test'} />;
    };
    const { container } = render(
      <ObjectivProvider tracker={tracker}>
        <ItemContextWrapper {...itemContextProps}>
          <TrackedIcon />
        </ItemContextWrapper>
      </ObjectivProvider>
    );

    jest.resetAllMocks();

    fireEvent.click(getByTestId(container, 'img'));

    expect(spyTransport.handle).toHaveBeenCalledTimes(1);
    expect(spyTransport.handle).toHaveBeenNthCalledWith(
      1,
      expect.objectContaining({
        _type: 'ClickEvent',
        location_stack: [
          expect.objectContaining({
            _type: 'ItemContext',
            ...itemContextProps,
          }),
        ],
      })
    );
  });

  it('should wrap the given children in a ItemContext (trigger via render-props)', () => {
    const spyTransport = { transportName: 'SpyTransport', handle: jest.fn(), isUsable: () => true };
    const tracker = new Tracker({ applicationId: 'app-id', transport: spyTransport });
    jest.spyOn(spyTransport, 'handle');

    const itemContextProps = { id: 'test-item' };
    const { container } = render(
      <ObjectivProvider tracker={tracker}>
        <ItemContextWrapper {...itemContextProps}>
          {(trackingContext) => (
            <img onClick={() => trackClickEvent(trackingContext)} data-testid={'img'} alt={'test'} />
          )}
        </ItemContextWrapper>
      </ObjectivProvider>
    );

    jest.resetAllMocks();

    fireEvent.click(getByTestId(container, 'img'));

    expect(spyTransport.handle).toHaveBeenCalledTimes(1);
    expect(spyTransport.handle).toHaveBeenNthCalledWith(
      1,
      expect.objectContaining({
        _type: 'ClickEvent',
        location_stack: [
          expect.objectContaining({
            _type: 'ItemContext',
            ...itemContextProps,
          }),
        ],
      })
    );
  });
});
