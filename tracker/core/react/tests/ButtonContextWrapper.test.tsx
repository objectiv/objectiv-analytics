/*
 * Copyright 2021 Objectiv B.V.
 */

import { Tracker } from '@objectiv/tracker-core';
import { fireEvent, getByText, render } from '@testing-library/react';
import { ButtonContextWrapper, LocationTree, ObjectivProvider, trackClickEvent, useClickEventTracker } from '../src';

describe('ButtonContextWrapper', () => {
  beforeEach(() => {
    jest.resetAllMocks();
    LocationTree.clear();
  });

  afterEach(() => {
    jest.resetAllMocks();
  });

  it('should wrap the given children in a ButtonContext (trigger via Component)', () => {
    const spyTransport = { transportName: 'SpyTransport', handle: jest.fn(), isUsable: () => true };
    const tracker = new Tracker({ applicationId: 'app-id', transport: spyTransport });
    jest.spyOn(spyTransport, 'handle');

    const buttonContextProps = { id: 'test-button', text: 'text' };
    const TrackedButton = () => {
      const trackClickEvent = useClickEventTracker();
      return <button onClick={trackClickEvent}>Trigger Event</button>;
    };
    const { container } = render(
      <ObjectivProvider tracker={tracker}>
        <ButtonContextWrapper {...buttonContextProps}>
          <TrackedButton />
        </ButtonContextWrapper>
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
            _type: 'ButtonContext',
            ...buttonContextProps,
          }),
        ],
      })
    );
  });

  it('should wrap the given children in a ButtonContext (trigger via render-props)', () => {
    const spyTransport = { transportName: 'SpyTransport', handle: jest.fn(), isUsable: () => true };
    const tracker = new Tracker({ applicationId: 'app-id', transport: spyTransport });
    jest.spyOn(spyTransport, 'handle');

    const buttonContextProps = { id: 'test-button', text: 'text' };
    const { container } = render(
      <ObjectivProvider tracker={tracker}>
        <ButtonContextWrapper {...buttonContextProps}>
          {(trackingContext) => <button onClick={() => trackClickEvent(trackingContext)}>Trigger Event</button>}
        </ButtonContextWrapper>
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
            _type: 'ButtonContext',
            ...buttonContextProps,
          }),
        ],
      })
    );
  });
});
