/*
 * Copyright 2022 Objectiv B.V.
 */

import { MockConsoleImplementation, LogTransport } from '@objectiv/testing-tools';
import { render } from '@testing-library/react-native';
import React from 'react';
import { Text } from 'react-native';
import {
  ReactNativeTracker,
  RootLocationContextWrapper,
  TrackedView,
  TrackedViewProps,
  TrackingContextProvider,
  useLocationStack,
} from '../src';

require('@objectiv/developer-tools');
globalThis.objectiv.devTools?.TrackerConsole.setImplementation(MockConsoleImplementation);

describe('TrackedView', () => {
  const logTransport = new LogTransport();
  jest.spyOn(logTransport, 'handle');
  const tracker = new ReactNativeTracker({ applicationId: 'app-id', transport: logTransport });
  jest.spyOn(console, 'debug').mockImplementation(jest.fn);

  const TestTrackedView = (props: TrackedViewProps & { testID?: string }) => (
    <TrackingContextProvider tracker={tracker}>
      <RootLocationContextWrapper id={'test'}>
        <TrackedView {...props} />
      </RootLocationContextWrapper>
    </TrackingContextProvider>
  );

  beforeEach(() => {
    jest.resetAllMocks();
  });

  const ViewChild = (props: { title: string }) => {
    const locationPath = globalThis.objectiv.devTools?.getLocationPath(useLocationStack());

    console.debug(locationPath);

    return (
      <Text>
        {props.title}:{locationPath}
      </Text>
    );
  };

  it('should wrap View in ContentContext', () => {
    render(
      <TestTrackedView id={'test-view'}>
        <ViewChild title={'Child'} />
      </TestTrackedView>
    );

    expect(console.debug).toHaveBeenCalledTimes(1);
    expect(console.debug).toHaveBeenNthCalledWith(1, 'RootLocation:test / Content:test-view');
  });
});
