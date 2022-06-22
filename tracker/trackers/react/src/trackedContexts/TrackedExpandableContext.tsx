/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { makeIdFromString } from '@objectiv/tracker-core';
import { ExpandableContextWrapper, trackVisibility, useLocationStack } from '@objectiv/tracker-react-core';
import React, { useRef } from 'react';
import { TrackedShowableContextProps } from '../types';

/**
 * Generates a new React Element already wrapped in an ExpandableContext.
 * Automatically tracks HiddenEvent and VisibleEvent based on the given `isVisible` prop.
 */
export const TrackedExpandableContext = React.forwardRef<HTMLElement, TrackedShowableContextProps>((props, ref) => {
  const { id, Component, forwardId = false, isVisible = false, normalizeId = true, ...otherProps } = props;
  const wasVisible = useRef<boolean>(isVisible);
  const locationStack = useLocationStack();

  let expandableId: string | null = id;
  if (normalizeId) {
    expandableId = makeIdFromString(expandableId);
  }

  const componentProps = {
    ...otherProps,
    ...(ref ? { ref } : {}),
    ...(forwardId ? { id } : {}),
  };

  if (!expandableId) {
    if (globalThis.objectiv.devTools) {
      const locationPath = globalThis.objectiv.devTools.getLocationPath(locationStack);
      globalThis.objectiv.devTools.TrackerConsole.error(
        `｢objectiv｣ Could not generate a valid id for ExpandableContext @ ${locationPath}. Please provide the \`id\` property.`
      );
    }
    return React.createElement(Component, componentProps);
  }

  return (
    <ExpandableContextWrapper id={expandableId}>
      {(trackingContext) => {
        if ((wasVisible.current && !isVisible) || (!wasVisible.current && isVisible)) {
          wasVisible.current = isVisible;
          trackVisibility({ isVisible, ...trackingContext });
        }
        return React.createElement(Component, componentProps);
      }}
    </ExpandableContextWrapper>
  );
});
