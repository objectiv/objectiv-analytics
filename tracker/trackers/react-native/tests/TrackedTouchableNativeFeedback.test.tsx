/*
 * Copyright 2022 Objectiv B.V.
 */

import { MockConsoleImplementation, SpyTransport } from '@objectiv/testing-tools';
import { LocationContextName } from '@objectiv/tracker-core';
import { fireEvent, render } from '@testing-library/react-native';
import React from 'react';
import { Text } from 'react-native';
import {
  ReactNativeTracker,
  RootLocationContextWrapper,
  TrackedTouchableNativeFeedback,
  TrackedTouchableNativeFeedbackProps,
  TrackingContextProvider,
} from '../src';

require('@objectiv/developer-tools');
globalThis.objectiv?.TrackerConsole.setImplementation(MockConsoleImplementation);

describe('TrackedTouchableNativeFeedback', () => {
  const spyTransport = new SpyTransport();
  jest.spyOn(spyTransport, 'handle');
  const tracker = new ReactNativeTracker({ applicationId: 'app-id', transport: spyTransport });

  const TestTrackedTouchableNativeFeedback = (props: TrackedTouchableNativeFeedbackProps & { testID?: string }) => (
    <TrackingContextProvider tracker={tracker}>
      <RootLocationContextWrapper id={'test'}>
        <TrackedTouchableNativeFeedback {...props} />
      </RootLocationContextWrapper>
    </TrackingContextProvider>
  );

  beforeEach(() => {
    jest.resetAllMocks();
  });

  it('should track PressEvent on press with a PressableContext in the LocationStack', () => {
    const { getByTestId } = render(
      <TestTrackedTouchableNativeFeedback testID="test-touchable-native-feedback">
        <Text>Trigger Event</Text>
      </TestTrackedTouchableNativeFeedback>
    );

    jest.resetAllMocks();

    fireEvent.press(getByTestId('test-touchable-native-feedback'));

    expect(spyTransport.handle).toHaveBeenCalledTimes(1);
    expect(spyTransport.handle).toHaveBeenCalledWith(
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
      <TestTrackedTouchableNativeFeedback testID="test-touchable-highlight">
        <Text>☹️</Text>
      </TestTrackedTouchableNativeFeedback>
    );

    jest.resetAllMocks();

    fireEvent.press(getByTestId('test-touchable-highlight'));

    expect(spyTransport.handle).not.toHaveBeenCalled();
  });

  it('should TrackerConsole.error if PressableContext id cannot be auto-detected', () => {
    render(
      <TestTrackedTouchableNativeFeedback testID="test-touchable-highlight">
        <Text>☹️</Text>
      </TestTrackedTouchableNativeFeedback>
    );

    expect(MockConsoleImplementation.error).toHaveBeenCalledTimes(1);
    expect(MockConsoleImplementation.error).toHaveBeenCalledWith(
      '｢objectiv｣ Could not generate a valid id for PressableContext @ RootLocation:test. Please provide the `id` property manually.'
    );
  });

  it('should execute onPress handler if specified', () => {
    const onPressSpy = jest.fn();
    const { getByTestId } = render(
      <TestTrackedTouchableNativeFeedback testID="test-touchable-highlight" onPress={onPressSpy}>
        <Text>touchable highlight</Text>
      </TestTrackedTouchableNativeFeedback>
    );

    fireEvent.press(getByTestId('test-touchable-highlight'));

    expect(onPressSpy).toHaveBeenCalledTimes(1);
  });

  describe('Without developer tools', () => {
    let objectivGlobal = globalThis.objectiv;

    beforeEach(() => {
      jest.clearAllMocks();
      globalThis.objectiv = undefined;
    });

    afterEach(() => {
      globalThis.objectiv = objectivGlobal;
    });

    it('should not TrackerConsole.error if PressableContext id cannot be auto-detected', () => {
      render(
        <TestTrackedTouchableNativeFeedback testID="test-touchable-highlight">
          <Text>☹️</Text>
        </TestTrackedTouchableNativeFeedback>
      );

      expect(MockConsoleImplementation.error).not.toHaveBeenCalled();
    });
  });
});
