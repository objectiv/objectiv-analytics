/*
 * Copyright 2022 Objectiv B.V.
 */

import { MockConsoleImplementation, SpyTransport } from '@objectiv/testing-tools';
import { render } from '@testing-library/react-native';
import React from 'react';
import { Text } from 'react-native';
import {
  ReactNativeTracker,
  RootLocationContextWrapper,
  TrackedSafeAreaView,
  TrackedSafeAreaViewProps,
  TrackingContextProvider,
  useLocationStack,
} from '../src';

require('@objectiv/developer-tools');
globalThis.objectiv?.TrackerConsole.setImplementation(MockConsoleImplementation);

describe('TrackedSafeAreaView', () => {
  const spyTransport = new SpyTransport();
  jest.spyOn(spyTransport, 'handle');
  const tracker = new ReactNativeTracker({ applicationId: 'app-id', transport: spyTransport });
  jest.spyOn(console, 'debug').mockImplementation(jest.fn);

  const TestTrackedSafeAreaView = (props: TrackedSafeAreaViewProps & { testID?: string }) => (
    <TrackingContextProvider tracker={tracker}>
      <RootLocationContextWrapper id={'test'}>
        <TrackedSafeAreaView {...props} />
      </RootLocationContextWrapper>
    </TrackingContextProvider>
  );

  beforeEach(() => {
    jest.resetAllMocks();
  });

  const SafeAreaViewChild = (props: { title: string }) => {
    const locationPath = globalThis.objectiv?.getLocationPath(useLocationStack());

    console.debug(locationPath);

    return (
      <Text>
        {props.title}:{locationPath}
      </Text>
    );
  };

  it('should wrap SafeAreaView in ContentContext', () => {
    render(
      <TestTrackedSafeAreaView id={'test-safe-area-view'}>
        <SafeAreaViewChild title={'Child'} />
      </TestTrackedSafeAreaView>
    );

    expect(console.debug).toHaveBeenCalledTimes(1);
    expect(console.debug).toHaveBeenNthCalledWith(1, 'RootLocation:test / Content:test-safe-area-view');
  });
});
