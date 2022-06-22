/*
 * Copyright 2022 Objectiv B.V.
 */

import { MockConsoleImplementation, LogTransport } from '@objectiv/testing-tools';
import { LocationContextName } from '@objectiv/tracker-core';
import { fireEvent, render } from '@testing-library/react-native';
import React from 'react';
import { Text } from 'react-native';
import {
  ReactNativeTracker,
  RootLocationContextWrapper,
  TrackedTouchableOpacity,
  TrackedTouchableOpacityProps,
  TrackingContextProvider,
} from '../src';

require('@objectiv/developer-tools');
globalThis.objectiv.devTools?.TrackerConsole.setImplementation(MockConsoleImplementation);

describe('TrackedTouchableOpacity', () => {
  const logTransport = new LogTransport();
  jest.spyOn(logTransport, 'handle');
  const tracker = new ReactNativeTracker({ applicationId: 'app-id', transport: logTransport });

  const TestTrackedTouchableOpacity = (props: TrackedTouchableOpacityProps & { testID?: string }) => (
    <TrackingContextProvider tracker={tracker}>
      <RootLocationContextWrapper id={'test'}>
        <TrackedTouchableOpacity {...props} />
      </RootLocationContextWrapper>
    </TrackingContextProvider>
  );

  beforeEach(() => {
    jest.resetAllMocks();
  });

  it('should track PressEvent on press with a PressableContext in the LocationStack', () => {
    const { getByTestId } = render(
      <TestTrackedTouchableOpacity testID="test-touchable-highlight">
        <Text>Trigger Event</Text>
      </TestTrackedTouchableOpacity>
    );

    jest.resetAllMocks();

    fireEvent.press(getByTestId('test-touchable-highlight'));

    expect(logTransport.handle).toHaveBeenCalledTimes(1);
    expect(logTransport.handle).toHaveBeenCalledWith(
      expect.objectContaining({
        _type: 'PressEvent',
        location_stack: expect.arrayContaining([
          expect.objectContaining({
            _type: LocationContextName.PressableContext,
            id: 'trigger-event',
          }),
        ]),
      })
    );
    expect(MockConsoleImplementation.error).not.toHaveBeenCalled();
  });

  it('should not track Button if PressableContext id cannot be auto-detected', () => {
    const { getByTestId } = render(
      <TestTrackedTouchableOpacity testID="test-touchable-highlight">
        <Text>☹️</Text>
      </TestTrackedTouchableOpacity>
    );

    jest.resetAllMocks();

    fireEvent.press(getByTestId('test-touchable-highlight'));

    expect(logTransport.handle).not.toHaveBeenCalled();
  });

  it('should TrackerConsole.error if PressableContext id cannot be auto-detected', () => {
    render(
      <TestTrackedTouchableOpacity testID="test-touchable-highlight">
        <Text>☹️</Text>
      </TestTrackedTouchableOpacity>
    );

    expect(MockConsoleImplementation.error).toHaveBeenCalledTimes(1);
    expect(MockConsoleImplementation.error).toHaveBeenCalledWith(
      '｢objectiv｣ Could not generate a valid id for PressableContext @ RootLocation:test. Please provide the `id` property manually.'
    );
  });

  it('should execute onPress handler if specified', () => {
    const onPressSpy = jest.fn();
    const { getByTestId } = render(
      <TestTrackedTouchableOpacity testID="test-touchable-opacity" onPress={onPressSpy}>
        <Text>touchable highlight</Text>
      </TestTrackedTouchableOpacity>
    );

    fireEvent.press(getByTestId('test-touchable-opacity'));

    expect(onPressSpy).toHaveBeenCalledTimes(1);
  });

  describe('Without developer tools', () => {
    let objectivGlobal = globalThis.objectiv;

    beforeEach(() => {
      jest.clearAllMocks();
      globalThis.objectiv.devTools = undefined;
    });

    afterEach(() => {
      globalThis.objectiv = objectivGlobal;
    });

    it('should not TrackerConsole.error if PressableContext id cannot be auto-detected', () => {
      render(
        <TestTrackedTouchableOpacity testID="test-touchable-highlight">
          <Text>☹️</Text>
        </TestTrackedTouchableOpacity>
      );

      expect(MockConsoleImplementation.error).not.toHaveBeenCalled();
    });
  });
});
