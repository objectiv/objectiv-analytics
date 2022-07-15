/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { LocationContextName, Tracker } from '@objectiv/tracker-core';
import { fireEvent, getByTestId, render } from '@testing-library/react';
import React from 'react';
import { InputContextWrapper, ObjectivProvider, trackInputChangeEvent, useInputChangeEventTracker } from '../src';

describe('InputContextWrapper', () => {
  beforeEach(() => {
    jest.resetAllMocks();
  });

  afterEach(() => {
    jest.resetAllMocks();
  });

  it('should wrap the given children in a InputContext (trigger via Component)', () => {
    const LogTransport = { transportName: 'LogTransport', handle: jest.fn(), isUsable: () => true };
    const tracker = new Tracker({ applicationId: 'app-id', transport: LogTransport });
    jest.spyOn(LogTransport, 'handle');

    const inputContextProps = { id: 'test-input' };
    const TrackedTextInput = () => {
      const trackInputChangeEvent = useInputChangeEventTracker();
      return <input data-testid="input" type="text" onBlur={() => trackInputChangeEvent()} />;
    };
    const { container } = render(
      <ObjectivProvider tracker={tracker}>
        <InputContextWrapper {...inputContextProps}>
          <TrackedTextInput />
        </InputContextWrapper>
      </ObjectivProvider>
    );

    jest.resetAllMocks();

    fireEvent.blur(getByTestId(container, 'input'));

    expect(LogTransport.handle).toHaveBeenCalledTimes(1);
    expect(LogTransport.handle).toHaveBeenNthCalledWith(
      1,
      expect.objectContaining({
        _type: 'InputChangeEvent',
        location_stack: [
          expect.objectContaining({
            _type: LocationContextName.InputContext,
            ...inputContextProps,
          }),
        ],
      })
    );
  });

  it('should wrap the given children in a InputContext (trigger via render-props)', () => {
    const LogTransport = { transportName: 'LogTransport', handle: jest.fn(), isUsable: () => true };
    const tracker = new Tracker({ applicationId: 'app-id', transport: LogTransport });
    jest.spyOn(LogTransport, 'handle');

    const inputContextProps = { id: 'test-input' };
    const { container } = render(
      <ObjectivProvider tracker={tracker}>
        <InputContextWrapper {...inputContextProps}>
          {(trackingContext) => <input data-testid="input" onBlur={() => trackInputChangeEvent(trackingContext)} />}
        </InputContextWrapper>
      </ObjectivProvider>
    );

    jest.resetAllMocks();

    fireEvent.blur(getByTestId(container, 'input'));

    expect(LogTransport.handle).toHaveBeenCalledTimes(1);
    expect(LogTransport.handle).toHaveBeenNthCalledWith(
      1,
      expect.objectContaining({
        _type: 'InputChangeEvent',
        location_stack: [
          expect.objectContaining({
            _type: LocationContextName.InputContext,
            ...inputContextProps,
          }),
        ],
      })
    );
  });
});
