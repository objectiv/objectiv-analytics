/*
 * Copyright 2022 Objectiv B.V.
 */

import { MockConsoleImplementation } from '@objectiv/testing-tools';
import { GlobalContextName, LocationContextName } from '@objectiv/tracker-core';
import {
  ContentContextWrapper,
  ObjectivProvider,
  ReactNativeTracker,
  RootLocationContextWrapper,
} from '@objectiv/tracker-react-native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { createNavigationContainerRef, NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import { fireEvent, render } from '@testing-library/react-native';
import React from 'react';
import { ContextsFromReactNavigationPlugin, TrackedLink, TrackedLinkProps } from '../src';

type TestParamList = {
  HomeScreen: undefined;
  DestinationScreen: { parameter: number };
};

require('@objectiv/developer-tools');
globalThis.objectiv.devTools?.TrackerConsole.setImplementation(MockConsoleImplementation);

describe('TrackedLink', () => {
  beforeEach(() => {
    globalThis.objectiv.TrackerRepository.trackersMap.clear();
    globalThis.objectiv.TrackerRepository.defaultTracker = undefined;
    jest.resetAllMocks();
  });

  const LogTransport = { transportName: 'LogTransport', handle: jest.fn(), isUsable: () => true };

  const cases: [
    TrackedLinkProps<TestParamList>,
    { id: string; href: string }, // LinkContext
    { id: string }, // RootLocationContext
    { id: string } // PathContext
  ][] = [
    [
      { to: '/DestinationScreen', children: 'test' },
      { id: 'test', href: '/DestinationScreen' },
      { id: 'HomeScreen' },
      { id: '/HomeScreen' },
    ],
    [
      { to: '/DestinationScreen', children: 'test', id: 'custom-id' },
      { id: 'custom-id', href: '/DestinationScreen' },
      { id: 'HomeScreen' },
      { id: '/HomeScreen' },
    ],
    [
      { to: '/DestinationScreen', children: '', id: 'custom-id' },
      { id: 'custom-id', href: '/DestinationScreen' },
      { id: 'HomeScreen' },
      { id: '/HomeScreen' },
    ],
    [
      { to: { screen: 'DestinationScreen' }, children: 'test' },
      { id: 'test', href: '/DestinationScreen' },
      { id: 'HomeScreen' },
      { id: '/HomeScreen' },
    ],
    [
      { to: { screen: 'DestinationScreen', params: { parameter: 123 } }, children: 'test' },
      { id: 'test', href: '/DestinationScreen?parameter=123' },
      { id: 'HomeScreen' },
      { id: '/HomeScreen' },
    ],
  ];

  cases.forEach(([linkProps, linkContext, rootLocationContext, pathContext]) => {
    it(`props: ${JSON.stringify(linkProps)} > LinkContext: ${JSON.stringify(linkContext)}`, () => {
      const navigationContainerRef = createNavigationContainerRef();
      const tracker = new ReactNativeTracker({
        applicationId: 'app-id',
        transport: LogTransport,
        plugins: [new ContextsFromReactNavigationPlugin({ navigationContainerRef })],
      });
      const Stack = createStackNavigator();
      const HomeScreen = () => <TrackedLink {...linkProps} testID="test" />;
      const DestinationScreen = () => <>yup</>;
      const { getByTestId } = render(
        <NavigationContainer ref={navigationContainerRef}>
          <ObjectivProvider tracker={tracker}>
            <Stack.Navigator>
              <Stack.Screen name="HomeScreen" component={HomeScreen} />
              <Stack.Screen name="DestinationScreen" component={DestinationScreen} />
            </Stack.Navigator>
          </ObjectivProvider>
        </NavigationContainer>
      );

      fireEvent.press(getByTestId('test'));

      expect(LogTransport.handle).toHaveBeenCalledTimes(2);
      expect(LogTransport.handle).toHaveBeenNthCalledWith(
        1,
        expect.objectContaining({
          _type: 'ApplicationLoadedEvent',
          global_contexts: [
            expect.objectContaining({ _type: GlobalContextName.ApplicationContext, id: 'app-id' }),
            expect.objectContaining({ _type: GlobalContextName.PathContext, ...pathContext }),
          ],
          location_stack: [
            expect.objectContaining({ _type: LocationContextName.RootLocationContext, ...rootLocationContext }),
          ],
        })
      );
      expect(LogTransport.handle).toHaveBeenNthCalledWith(
        2,
        expect.objectContaining({
          _type: 'PressEvent',
          global_contexts: [
            expect.objectContaining({ _type: GlobalContextName.ApplicationContext, id: 'app-id' }),
            expect.objectContaining({ _type: GlobalContextName.PathContext, ...pathContext }),
          ],
          location_stack: [
            expect.objectContaining({ _type: LocationContextName.RootLocationContext, ...rootLocationContext }),
            expect.objectContaining({ _type: LocationContextName.LinkContext, ...linkContext }),
          ],
        })
      );
    });
  });

  it('should console.error if an id cannot be automatically generated', () => {
    const tracker = new ReactNativeTracker({ applicationId: 'app-id', transport: LogTransport });

    const Stack = createStackNavigator();
    const HomeScreen = () => (
      <ContentContextWrapper id="content">
        <TrackedLink to="/HomeScreen">🏡</TrackedLink>
      </ContentContextWrapper>
    );
    const DestinationScreen = () => <>yup</>;
    const navigationContainerRef = createNavigationContainerRef();
    render(
      <NavigationContainer ref={navigationContainerRef}>
        <ObjectivProvider tracker={tracker}>
          <RootLocationContextWrapper id="root">
            <Stack.Navigator>
              <Stack.Screen name="HomeScreen" component={HomeScreen} />
              <Stack.Screen name="DestinationScreen" component={DestinationScreen} />
            </Stack.Navigator>
          </RootLocationContextWrapper>
        </ObjectivProvider>
      </NavigationContainer>
    );

    expect(MockConsoleImplementation.error).toHaveBeenCalledTimes(1);
    expect(MockConsoleImplementation.error).toHaveBeenCalledWith(
      '｢objectiv｣ Could not generate a valid id for PressableContext @ RootLocation:root / Content:content. Please provide the `id` property manually.'
    );
  });

  it('should execute the given onPress as well', async () => {
    const tracker = new ReactNativeTracker({ applicationId: 'app-id', transport: LogTransport });
    const onPressSpy = jest.fn();

    const Stack = createStackNavigator();
    const HomeScreen = () => (
      <TrackedLink testID="test" to="/HomeScreen" onPress={onPressSpy}>
        Press me!
      </TrackedLink>
    );
    const DestinationScreen = () => <>yup</>;
    const navigationContainerRef = createNavigationContainerRef();
    const { getByTestId } = render(
      <NavigationContainer ref={navigationContainerRef}>
        <ObjectivProvider tracker={tracker}>
          <Stack.Navigator>
            <Stack.Screen name="HomeScreen" component={HomeScreen} />
            <Stack.Screen name="DestinationScreen" component={DestinationScreen} />
          </Stack.Navigator>
        </ObjectivProvider>
      </NavigationContainer>
    );

    fireEvent.press(getByTestId('test'));

    expect(onPressSpy).toHaveBeenCalledTimes(1);
  });

  it('should fallback to RootLocationContext:home when there is no current route', async () => {
    const navigationContainerRef = createNavigationContainerRef();
    jest.spyOn(navigationContainerRef, 'isReady').mockImplementation(() => true);
    jest.spyOn(navigationContainerRef, 'getCurrentRoute').mockImplementation(() => ({ key: '', name: '' }));
    jest.spyOn(navigationContainerRef, 'getRootState').mockReturnValue({
      stale: false,
      type: 'stack',
      key: 'stack-G-JBZpD12CtdWhBvSopmt',
      index: 0,
      routeNames: ['Home', 'Profile', 'Settings'],
      routes: [
        {
          key: 'Home-uxvCOehGcN7D7h6kyuoS6',
          name: 'Home',
          state: {
            stale: false,
            type: 'tab',
            key: 'tab-DdYflY-1psGAlBpwT8DUu',
            index: 1,
            routeNames: ['Feed', 'Messages'],
            routes: [
              { name: 'Feed', key: 'Feed-nvDuU_obRSW5XMiF-EtBd' },
              { name: 'Messages', key: 'Messages-Qi2b8Z05GhfRVY7mf8Ei9' },
            ],
          },
        },
      ],
    });
    const testContextsFromReactNavigationPlugin = new ContextsFromReactNavigationPlugin({ navigationContainerRef });

    const contexts = { location_stack: [], global_contexts: [] };
    testContextsFromReactNavigationPlugin.enrich(contexts);

    expect(contexts.location_stack).toEqual([
      expect.objectContaining({ _type: LocationContextName.RootLocationContext, id: 'home' }),
    ]);
  });

  it('should fallback to defaults when navigationContainerRef is not ready', async () => {
    const navigationContainerRef = createNavigationContainerRef();
    jest.spyOn(navigationContainerRef, 'isReady').mockImplementation(() => false);
    const testContextsFromReactNavigationPlugin = new ContextsFromReactNavigationPlugin({ navigationContainerRef });

    const contexts = { location_stack: [], global_contexts: [] };
    testContextsFromReactNavigationPlugin.enrich(contexts);

    expect(contexts.location_stack).toEqual([
      expect.objectContaining({ _type: LocationContextName.RootLocationContext, id: 'home' }),
    ]);
    expect(contexts.global_contexts).toEqual([
      expect.objectContaining({ _type: GlobalContextName.PathContext, id: '/' }),
    ]);
  });

  it('should correctly generate RootLocation and Path Contexts with nested navigators', async () => {
    const navigationContainerRef = createNavigationContainerRef();
    const tracker = new ReactNativeTracker({
      applicationId: 'app-id',
      transport: LogTransport,
      plugins: [new ContextsFromReactNavigationPlugin({ navigationContainerRef })],
    });
    const Tab = createBottomTabNavigator();
    const Stack = createStackNavigator();

    /**
     * Example taken from here: https://reactnavigation.org/docs/nesting-navigators
     * Stack.Navigator
     *   Home (Tab.Navigator)
     *     Feed (Screen)
     *     Messages (Screen)
     *   Profile (Screen)
     *   Settings (Screen)
     */

    const Feed = () => (
      <TrackedLink testID="go-to-home-from-feed" to="/Home">
        Go to Home
      </TrackedLink>
    );

    const Messages = () => (
      <TrackedLink testID="go-to-home-from-messages" to="/Home">
        Go to Home
      </TrackedLink>
    );

    const Profile = () => (
      <TrackedLink testID="go-to-home-from-profile" to="/Home">
        Go to Home
      </TrackedLink>
    );

    const Settings = () => (
      <TrackedLink testID="go-to-home-from-settings" to="/Home">
        Go to Home
      </TrackedLink>
    );

    const Home = () => (
      <Tab.Navigator initialRouteName={'Messages'}>
        <Tab.Screen name="Feed" component={Feed} />
        <Tab.Screen name="Messages" component={Messages} />
      </Tab.Navigator>
    );

    const { getByTestId } = render(
      <NavigationContainer ref={navigationContainerRef}>
        <ObjectivProvider tracker={tracker}>
          <Stack.Navigator initialRouteName={'Home'}>
            <Stack.Screen name="Home" component={Home} />
            <Stack.Screen name="Profile" component={Profile} />
            <Stack.Screen name="Settings" component={Settings} />
          </Stack.Navigator>
        </ObjectivProvider>
      </NavigationContainer>
    );

    fireEvent.press(getByTestId('go-to-home-from-messages'));

    expect(LogTransport.handle).toHaveBeenCalledTimes(2);
    expect(LogTransport.handle).toHaveBeenNthCalledWith(
      1,
      expect.objectContaining({
        _type: 'ApplicationLoadedEvent',
        global_contexts: [
          expect.objectContaining({ _type: GlobalContextName.ApplicationContext, id: 'app-id' }),
          expect.objectContaining({ _type: GlobalContextName.PathContext, id: '/Home/Messages' }),
        ],
        location_stack: [expect.objectContaining({ _type: LocationContextName.RootLocationContext, id: 'Messages' })],
      })
    );
    expect(LogTransport.handle).toHaveBeenNthCalledWith(
      2,
      expect.objectContaining({
        _type: 'PressEvent',
        global_contexts: [
          expect.objectContaining({ _type: GlobalContextName.ApplicationContext, id: 'app-id' }),
          expect.objectContaining({ _type: GlobalContextName.PathContext, id: '/Home/Messages' }),
        ],
        location_stack: [
          expect.objectContaining({ _type: LocationContextName.RootLocationContext, id: 'Messages' }),
          expect.objectContaining({ _type: LocationContextName.LinkContext, id: 'go-to-home', href: '/Home' }),
        ],
      })
    );
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

    it('should fail silently if an id cannot be automatically generated', () => {
      const tracker = new ReactNativeTracker({ applicationId: 'app-id', transport: LogTransport });

      const Stack = createStackNavigator();
      const HomeScreen = () => (
        <ContentContextWrapper id="content">
          <TrackedLink to="/HomeScreen">🏡</TrackedLink>
        </ContentContextWrapper>
      );
      const DestinationScreen = () => <>yup</>;
      const navigationContainerRef = createNavigationContainerRef();
      render(
        <NavigationContainer ref={navigationContainerRef}>
          <ObjectivProvider tracker={tracker}>
            <RootLocationContextWrapper id="root">
              <Stack.Navigator>
                <Stack.Screen name="HomeScreen" component={HomeScreen} />
                <Stack.Screen name="DestinationScreen" component={DestinationScreen} />
              </Stack.Navigator>
            </RootLocationContextWrapper>
          </ObjectivProvider>
        </NavigationContainer>
      );

      expect(MockConsoleImplementation.error).not.toHaveBeenCalled();
    });
  });
});
