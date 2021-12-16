/*
 * Copyright 2021 Objectiv B.V.
 */

import { Tracker } from '@objectiv/tracker-core';
import { fireEvent, getByTestId, render } from '@testing-library/react';
import {
  InputContextWrapper,
  LocationTree,
  ObjectivProvider,
  trackInputChangeEvent,
  useInputChangeEventTracker,
} from '../src';

describe('InputContextWrapper', () => {
  beforeEach(() => {
    jest.resetAllMocks();
    LocationTree.clear();
  });

  afterEach(() => {
    jest.resetAllMocks();
  });

  it('should wrap the given children in a InputContext (trigger via Component)', () => {
    const spyTransport = { transportName: 'SpyTransport', handle: jest.fn(), isUsable: () => true };
    const tracker = new Tracker({ applicationId: 'app-id', transport: spyTransport });
    jest.spyOn(spyTransport, 'handle');

    const inputContextProps = { id: 'test-input' };
    const TrackedTextInput = () => {
      const trackInputChangeEvent = useInputChangeEventTracker();
      return <input data-testid="input" type="text" onBlur={trackInputChangeEvent} />;
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

    expect(spyTransport.handle).toHaveBeenCalledTimes(1);
    expect(spyTransport.handle).toHaveBeenNthCalledWith(
      1,
      expect.objectContaining({
        _type: 'InputChangeEvent',
        location_stack: [
          expect.objectContaining({
            _type: 'InputContext',
            ...inputContextProps,
          }),
        ],
      })
    );
  });

  it('should wrap the given children in a InputContext (trigger via render-props)', () => {
    const spyTransport = { transportName: 'SpyTransport', handle: jest.fn(), isUsable: () => true };
    const tracker = new Tracker({ applicationId: 'app-id', transport: spyTransport });
    jest.spyOn(spyTransport, 'handle');

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

    expect(spyTransport.handle).toHaveBeenCalledTimes(1);
    expect(spyTransport.handle).toHaveBeenNthCalledWith(
      1,
      expect.objectContaining({
        _type: 'InputChangeEvent',
        location_stack: [
          expect.objectContaining({
            _type: 'InputContext',
            ...inputContextProps,
          }),
        ],
      })
    );
  });
});
