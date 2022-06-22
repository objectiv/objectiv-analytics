/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { makeIdFromString } from '@objectiv/tracker-core';
import { OverlayContextWrapper, trackVisibility, useLocationStack } from '@objectiv/tracker-react-core';
import React, { useRef } from 'react';
import { TrackedShowableContextProps } from '../types';

/**
 * Generates a new React Element already wrapped in an OverlayContext.
 * Automatically tracks HiddenEvent and VisibleEvent based on the given `isVisible` prop.
 */
export const TrackedOverlayContext = React.forwardRef<HTMLElement, TrackedShowableContextProps>((props, ref) => {
  const { id, Component, forwardId = false, isVisible = false, normalizeId = true, ...otherProps } = props;
  const wasVisible = useRef<boolean>(isVisible);
  const locationStack = useLocationStack();

  let overlayId: string | null = id;
  if (normalizeId) {
    overlayId = makeIdFromString(overlayId);
  }

  const componentProps = {
    ...otherProps,
    ...(ref ? { ref } : {}),
    ...(forwardId ? { id } : {}),
  };

  if (!overlayId) {
    if (globalThis.objectiv.devTools) {
      const locationPath = globalThis.objectiv.devTools.getLocationPath(locationStack);
      globalThis.objectiv.devTools.TrackerConsole.error(
        `｢objectiv｣ Could not generate a valid id for OverlayContext @ ${locationPath}. Please provide the \`id\` property.`
      );
    }
    return React.createElement(Component, componentProps);
  }

  return (
    <OverlayContextWrapper id={overlayId}>
      {(trackingContext) => {
        if ((wasVisible.current && !isVisible) || (!wasVisible.current && isVisible)) {
          wasVisible.current = isVisible;
          trackVisibility({ isVisible, ...trackingContext });
        }
        return React.createElement(Component, componentProps);
      }}
    </OverlayContextWrapper>
  );
});
