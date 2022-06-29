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
  TrackedVirtualizedList,
  TrackedVirtualizedListProps,
  TrackingContextProvider,
  useLocationStack,
} from '../src';

require('@objectiv/developer-tools');
globalThis.objectiv.devTools?.TrackerConsole.setImplementation(MockConsoleImplementation);

describe('TrackedVirtualizedList', () => {
  const logTransport = new LogTransport();
  jest.spyOn(logTransport, 'handle');
  const tracker = new ReactNativeTracker({ applicationId: 'app-id', transport: logTransport });
  jest.spyOn(console, 'debug').mockImplementation(jest.fn);

  type ListItemType = {
    id: string;
    title: string;
  };
  const data: ListItemType[] = [
    {
      id: 'bd7acbea-c1b1-46c2-aed5-3ad53abb28ba',
      title: 'First Item',
    },
    {
      id: '3ac68afc-c605-48d3-a4f8-fbd91aa97f63',
      title: 'Second Item',
    },
    {
      id: '58694a0f-3da1-471f-bd96-145571e29d72',
      title: 'Third Item',
    },
  ];

  const TestTrackedVirtualizedList = (props: TrackedVirtualizedListProps<ListItemType> & { testID?: string }) => (
    <TrackingContextProvider tracker={tracker}>
      <RootLocationContextWrapper id={'test'}>
        <TrackedVirtualizedList {...props} />
      </RootLocationContextWrapper>
    </TrackingContextProvider>
  );

  beforeEach(() => {
    jest.resetAllMocks();
  });

  const ListItem = (props: ListItemType) => {
    const locationPath = globalThis.objectiv.devTools?.getLocationPath(useLocationStack());

    console.debug(locationPath);

    return (
      <Text>
        {props.title}:{locationPath}
      </Text>
    );
  };

  it('should wrap VirtualizedList in ContentContext', () => {
    render(
      <TestTrackedVirtualizedList
        id={'test-virtualized-list'}
        data={data}
        renderItem={({ item }) => <ListItem {...item} />}
        keyExtractor={(item) => item.id}
        testID="test-virtualized-list"
        getItem={(data, index) => data[index]}
        getItemCount={() => data.length}
      />
    );

    expect(console.debug).toHaveBeenCalledTimes(3);
    expect(console.debug).toHaveBeenNthCalledWith(1, 'RootLocation:test / Content:test-virtualized-list');
    expect(console.debug).toHaveBeenNthCalledWith(2, 'RootLocation:test / Content:test-virtualized-list');
    expect(console.debug).toHaveBeenNthCalledWith(3, 'RootLocation:test / Content:test-virtualized-list');
  });
});
