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
  TrackedSectionList,
  TrackedSectionListProps,
  TrackingContextProvider,
  useLocationStack,
} from '../src';

require('@objectiv/developer-tools');
globalThis.objectiv.devTools?.TrackerConsole.setImplementation(MockConsoleImplementation);

describe('TrackedSectionList', () => {
  const logTransport = new LogTransport();
  jest.spyOn(logTransport, 'handle');
  const tracker = new ReactNativeTracker({ applicationId: 'app-id', transport: logTransport });
  jest.spyOn(console, 'debug').mockImplementation(jest.fn);

  type ListItemType = string;
  type SectionType = {
    title: string;
    data: string[];
  };
  const sections: SectionType[] = [
    {
      title: 'Main dishes',
      data: ['Pizza', 'Burger', 'Risotto'],
    },
    {
      title: 'Sides',
      data: ['French Fries', 'Onion Rings', 'Fried Shrimps'],
    },
    {
      title: 'Drinks',
      data: ['Water', 'Coke', 'Beer'],
    },
    {
      title: 'Desserts',
      data: ['Cheese Cake', 'Ice Cream'],
    },
  ];

  const TestTrackedSectionList = (props: TrackedSectionListProps<ListItemType> & { testID?: string }) => (
    <TrackingContextProvider tracker={tracker}>
      <RootLocationContextWrapper id={'test'}>
        <TrackedSectionList {...props} />
      </RootLocationContextWrapper>
    </TrackingContextProvider>
  );

  beforeEach(() => {
    jest.resetAllMocks();
  });

  const ListItem = (props: { text: ListItemType }) => {
    const locationPath = globalThis.objectiv.devTools?.getLocationPath(useLocationStack());

    console.debug(locationPath);

    return (
      <Text>
        {props.text}:{locationPath}
      </Text>
    );
  };

  it('should wrap SectionList in ContentContext', () => {
    render(
      <TestTrackedSectionList
        id={'test-section-list'}
        sections={sections}
        renderItem={({ item }) => <ListItem text={item} />}
        renderSectionHeader={({ section: { title } }) => <Text>{title}</Text>}
        keyExtractor={(item, index) => item + index}
        testID="test-section-list"
        initialNumToRender={2}
      />
    );

    expect(console.debug).toHaveBeenCalledTimes(1);
    expect(console.debug).toHaveBeenNthCalledWith(1, 'RootLocation:test / Content:test-section-list');
  });
});
