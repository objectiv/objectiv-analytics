/*
 * Copyright 2022 Objectiv B.V.
 */

import { LinkContextWrapper, trackPressEvent, useLocationStack } from '@objectiv/tracker-react-core';
import { NavigationAction } from '@react-navigation/core';
import { Link } from '@react-navigation/native';
import { To } from '@react-navigation/native/lib/typescript/src/useLinkTo';
import React from 'react';
import { GestureResponderEvent, TextProps } from 'react-native';
import { makeLinkContextProps } from './makeLinkContextProps';

/**
 * The original Props type definition of React Navigation Link.
 */
export type Props<ParamList extends ReactNavigation.RootParamList> = {
  to: To<ParamList>;
  action?: NavigationAction;
  target?: string;
  onPress?: (e: React.MouseEvent<HTMLAnchorElement, MouseEvent> | GestureResponderEvent) => void;
} & (TextProps & { children: React.ReactNode });

/**
 * TrackedLink has the same props of Link with an additional optional `id` prop.
 */
export type TrackedLinkProps<ParamList extends ReactNavigation.RootParamList> = Props<ParamList> & {
  /**
   * Optional. Auto-generated from `title`. Used to set a LinkContext `id` manually.
   */
  id?: string;
};

/**
 * A Link already wrapped in LinkContext automatically tracking PressEvent.
 */
export function TrackedLink<ParamList extends ReactNavigation.RootParamList>(props: TrackedLinkProps<ParamList>) {
  const { id, ...linkProps } = props;

  // Generate LinkContext props from props.
  const { contextId, contextHref } = makeLinkContextProps(props);

  // If we couldn't generate an `id`, log the issue and return an untracked Link.
  const locationStack = useLocationStack();
  if (!contextId) {
    if (globalThis.objectiv.devTools) {
      const locationPath = globalThis.objectiv.devTools.getLocationPath(locationStack);
      globalThis.objectiv.devTools.TrackerConsole.error(
        `｢objectiv｣ Could not generate a valid id for PressableContext @ ${locationPath}. Please provide the \`id\` property manually.`
      );
    }
    return <Link<ParamList> {...linkProps} />;
  }

  return (
    <LinkContextWrapper id={contextId} href={contextHref}>
      {(trackingContext) => (
        <Link<ParamList>
          {...linkProps}
          onPress={(event) => {
            trackPressEvent(trackingContext);
            props.onPress && props.onPress(event);
          }}
        />
      )}
    </LinkContextWrapper>
  );
}
