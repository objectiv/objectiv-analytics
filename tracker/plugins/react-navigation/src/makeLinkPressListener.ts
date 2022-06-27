/*
 * Copyright 2022 Objectiv B.V.
 */

import { makeLinkContext } from '@objectiv/tracker-core';
import { TrackingContext, trackPressEvent } from '@objectiv/tracker-react-core';
import { findFocusedRoute, NavigationState } from '@react-navigation/native';

/**
 * The parameters of makeLinkPressListener.
 */
export type makeLinkPressListenerParameters = {
  /**
   * The TrackingContext of the closest wrapped Component.
   */
  trackingContext: TrackingContext;

  /**
   * The navigation object to be retrieved from the listeners prop.
   */
  navigation: {
    /**
     * We don't need anything but getState.
     */
    getState: () => NavigationState;
  };

  /**
   * Optional. If we can't retrieve a route name this parameter will be used instead as LinkContext id.
   */
  id?: string;
};

/**
 * Generates a press listener that automatically infers a LinkContext from the given navigation.
 */
export const makeLinkPressListener = ({ trackingContext, navigation, id }: makeLinkPressListenerParameters) => {
  return ({ target }: { target?: string }) => {
    const navigationState = navigation.getState();
    const currentRoute = findFocusedRoute(navigationState);
    const linkContextId = id ?? currentRoute?.name;
    const linkContextHref = `/${navigationState.routes.find(({ key }) => key === target)?.name}`;

    if (!linkContextId) {
      globalThis.objectiv.devTools?.TrackerConsole.error(
        `｢objectiv:makePressListener｣ Could not retrieve a valid id for LinkContext in ${
          navigationState.type
        } navigator with routes: ${navigationState.routeNames.join(', ')}. Please provide the \`id\` parameter.`
      );
      return;
    }

    trackPressEvent({
      ...trackingContext,
      locationStack: [
        ...trackingContext.locationStack,
        makeLinkContext({
          id: linkContextId,
          href: linkContextHref,
        }),
      ],
    });
  };
};
