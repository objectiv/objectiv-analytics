/*
 * Copyright 2022 Objectiv B.V.
 */

import { MockConsoleImplementation } from '@objectiv/testing-tools';
import { GlobalContextName, LocationContextName } from '@objectiv/tracker-core';
import {
  NavigationContextWrapper,
  ObjectivProvider,
  ReactNativeTracker,
  TrackingContext,
} from '@objectiv/tracker-react-native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { NavigationContainer, NavigationState } from '@react-navigation/native';
import { fireEvent, render } from '@testing-library/react-native';
import React from 'react';
import { Text } from 'react-native';
import { makeLinkPressListener } from '../src/makeLinkPressListener';

require('@objectiv/developer-tools');
globalThis.objectiv?.TrackerConsole.setImplementation(MockConsoleImplementation);

describe('makePressListener', () => {
  beforeEach(() => {
    jest.resetAllMocks();
  });

  const spyTransport = { transportName: 'SpyTransport', handle: jest.fn(), isUsable: () => true };

  it('should correctly generate LinkContext for the pressed BottomTabItems', async () => {
    const tracker = new ReactNativeTracker({
      applicationId: 'app-id',
      transport: spyTransport,
    });
    const Tab = createBottomTabNavigator();

    const { getByTestId } = render(
      <NavigationContainer>
        <ObjectivProvider tracker={tracker}>
          <NavigationContextWrapper id={'bottom-tabs'}>
            {(trackingContext) => (
              <Tab.Navigator>
                <Tab.Screen
                  options={{ tabBarTestID: 'TabA ' }}
                  name="ScreenA"
                  listeners={({ navigation }) => ({
                    tabPress: makeLinkPressListener({ trackingContext, navigation }),
                  })}
                >
                  {() => <Text>Screen A</Text>}
                </Tab.Screen>
                <Tab.Screen
                  options={{ tabBarTestID: 'TabB ' }}
                  name="ScreenB"
                  listeners={({ navigation }) => ({
                    tabPress: makeLinkPressListener({ trackingContext, navigation }),
                  })}
                >
                  {() => <Text>Screen B</Text>}
                </Tab.Screen>
              </Tab.Navigator>
            )}
          </NavigationContextWrapper>
        </ObjectivProvider>
      </NavigationContainer>
    );

    fireEvent.press(getByTestId('TabB'));
    fireEvent.press(getByTestId('TabA'));

    expect(spyTransport.handle).toHaveBeenCalledTimes(3);
    expect(spyTransport.handle).toHaveBeenNthCalledWith(
      1,
      expect.objectContaining({
        _type: 'ApplicationLoadedEvent',
        global_contexts: [expect.objectContaining({ _type: GlobalContextName.ApplicationContext, id: 'app-id' })],
      })
    );
    expect(spyTransport.handle).toHaveBeenNthCalledWith(
      2,
      expect.objectContaining({
        _type: 'PressEvent',
        global_contexts: [expect.objectContaining({ _type: GlobalContextName.ApplicationContext, id: 'app-id' })],
        location_stack: [
          expect.objectContaining({ _type: LocationContextName.NavigationContext, id: 'bottom-tabs' }),
          expect.objectContaining({ _type: LocationContextName.LinkContext, id: 'ScreenA', href: '/ScreenB' }),
        ],
      })
    );
    expect(spyTransport.handle).toHaveBeenNthCalledWith(
      3,
      expect.objectContaining({
        _type: 'PressEvent',
        global_contexts: [expect.objectContaining({ _type: GlobalContextName.ApplicationContext, id: 'app-id' })],
        location_stack: [
          expect.objectContaining({ _type: LocationContextName.NavigationContext, id: 'bottom-tabs' }),
          expect.objectContaining({ _type: LocationContextName.LinkContext, id: 'ScreenB', href: '/ScreenA' }),
        ],
      })
    );
  });

  it('should console.error if an id cannot be automatically generated', () => {
    const tracker = new ReactNativeTracker({
      applicationId: 'app-id',
      transport: spyTransport,
    });
    const trackingContext: TrackingContext = {
      locationStack: [],
      tracker,
    };
    const navigation = {
      getState: (): NavigationState => ({
        stale: false,
        type: 'tab',
        key: 'stack-G-JBZpD12CtdWhBvSopmt',
        index: 0,
        routeNames: ['Home', 'Profile', 'Settings'],
        routes: [
          {
            key: 'Home-uxvCOehGcN7D7h6kyuoS6',
            name: '',
          },
        ],
      }),
    };

    makeLinkPressListener({ trackingContext, navigation })({ target: 'Home' });

    expect(MockConsoleImplementation.error).toHaveBeenCalledTimes(1);
    expect(MockConsoleImplementation.error).toHaveBeenCalledWith(
      '｢objectiv:makePressListener｣ Could not retrieve a valid id for LinkContext in tab navigator with routes: Home, Profile, Settings. Please provide the `id` parameter.'
    );

    jest.resetAllMocks();

    makeLinkPressListener({ trackingContext, navigation, id: 'yep' })({ target: 'Home' });

    expect(MockConsoleImplementation.error).not.toHaveBeenCalled();
  });
});
