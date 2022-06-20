/*
 * Copyright 2022 Objectiv B.V.
 */

import { MockConsoleImplementation, SpyTransport } from '@objectiv/testing-tools';
import { LocationContextName } from '@objectiv/tracker-core';
import { fireEvent, render } from '@testing-library/react-native';
import React from 'react';
import {
  ReactNativeTracker,
  RootLocationContextWrapper,
  TrackedSwitch,
  TrackedSwitchProps,
  TrackingContextProvider,
} from '../src';

require('@objectiv/developer-tools');
globalThis.objectiv.devTools?.TrackerConsole.setImplementation(MockConsoleImplementation);

describe('TrackedSwitch', () => {
  const spyTransport = new SpyTransport();
  jest.spyOn(spyTransport, 'handle');
  const tracker = new ReactNativeTracker({ applicationId: 'app-id', transport: spyTransport });

  const TestTrackedSwitch = (props: TrackedSwitchProps & { testID?: string }) => (
    <TrackingContextProvider tracker={tracker}>
      <RootLocationContextWrapper id={'test'}>
        <TrackedSwitch {...props} />
      </RootLocationContextWrapper>
    </TrackingContextProvider>
  );

  beforeEach(() => {
    jest.resetAllMocks();
  });

  it('should track InputChangeEvent on press with a InputContext in the LocationStack', () => {
    const { getByTestId } = render(<TestTrackedSwitch id={'test-switch'} testID="test-switch" />);

    jest.resetAllMocks();

    fireEvent(getByTestId('test-switch'), 'valueChange', true);

    expect(spyTransport.handle).toHaveBeenCalledTimes(1);
    expect(spyTransport.handle).toHaveBeenCalledWith(
      expect.objectContaining({
        _type: 'InputChangeEvent',
        location_stack: expect.arrayContaining([
          expect.objectContaining({
            _type: LocationContextName.InputContext,
            id: 'test-switch',
          }),
        ]),
      })
    );
    expect(MockConsoleImplementation.error).not.toHaveBeenCalled();
  });

  it('should execute onValueChange handler if specified', () => {
    const onValueChangeSpy = jest.fn();
    const { getByTestId } = render(
      <TestTrackedSwitch id={'test-switch'} testID="test-switch" onValueChange={onValueChangeSpy} />
    );

    fireEvent(getByTestId('test-switch'), 'valueChange', true);

    expect(onValueChangeSpy).toHaveBeenCalledTimes(1);
  });
});
