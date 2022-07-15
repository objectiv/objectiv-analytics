/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { LocationContextName, Tracker } from '@objectiv/tracker-core';
import { fireEvent, getByText, render } from '@testing-library/react';
import React from 'react';
import { PressableContextWrapper, ObjectivProvider, trackPressEvent, usePressEventTracker } from '../src';

describe('PressableContextWrapper', () => {
  beforeEach(() => {
    jest.resetAllMocks();
  });

  afterEach(() => {
    jest.resetAllMocks();
  });

  it('should wrap the given children in a PressableContext (trigger via Component)', () => {
    const LogTransport = { transportName: 'LogTransport', handle: jest.fn(), isUsable: () => true };
    const tracker = new Tracker({ applicationId: 'app-id', transport: LogTransport });
    jest.spyOn(LogTransport, 'handle');

    const buttonContextProps = { id: 'test-button' };
    const TrackedButton = () => {
      const trackPressEvent = usePressEventTracker();
      return <button onClick={() => trackPressEvent()}>Trigger Event</button>;
    };
    const { container } = render(
      <ObjectivProvider tracker={tracker}>
        <PressableContextWrapper {...buttonContextProps}>
          <TrackedButton />
        </PressableContextWrapper>
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
            _type: LocationContextName.PressableContext,
            ...buttonContextProps,
          }),
        ],
      })
    );
  });

  it('should wrap the given children in a PressableContext (trigger via render-props)', () => {
    const LogTransport = { transportName: 'LogTransport', handle: jest.fn(), isUsable: () => true };
    const tracker = new Tracker({ applicationId: 'app-id', transport: LogTransport });
    jest.spyOn(LogTransport, 'handle');

    const buttonContextProps = { id: 'test-button' };
    const { container } = render(
      <ObjectivProvider tracker={tracker}>
        <PressableContextWrapper {...buttonContextProps}>
          {(trackingContext) => <button onClick={() => trackPressEvent(trackingContext)}>Trigger Event</button>}
        </PressableContextWrapper>
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
            _type: LocationContextName.PressableContext,
            ...buttonContextProps,
          }),
        ],
      })
    );
  });
});
