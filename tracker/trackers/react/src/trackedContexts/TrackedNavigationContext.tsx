/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { makeIdFromString } from "@objectiv/tracker-core";
import { NavigationContextWrapper, useLocationStack } from '@objectiv/tracker-react-core';
import React from 'react';
import { TrackedContextProps } from '../types';

/**
 * Generates a new React Element already wrapped in a NavigationContext.
 */
export const TrackedNavigationContext = React.forwardRef<HTMLElement, TrackedContextProps>((props, ref) => {
  const { id, Component, forwardId = false, normalizeId = true, ...otherProps } = props;
  const locationStack = useLocationStack();

  let navigationId: string | null = id;
  if(normalizeId) {
    navigationId = makeIdFromString(navigationId);
  }

  const componentProps = {
    ...otherProps,
    ...(ref ? { ref } : {}),
    ...(forwardId ? { id } : {}),
  };

  if (!navigationId) {
    if (globalThis.objectiv) {
      const locationPath = globalThis.objectiv.getLocationPath(locationStack);
      globalThis.objectiv.TrackerConsole.error(
        `｢objectiv｣ Could not generate a valid id for NavigationContext @ ${locationPath}. Please provide the \`id\` property.`
      );
    }
    return React.createElement(Component, componentProps);
  }

  return <NavigationContextWrapper id={navigationId}>{React.createElement(Component, componentProps)}</NavigationContextWrapper>;
});
