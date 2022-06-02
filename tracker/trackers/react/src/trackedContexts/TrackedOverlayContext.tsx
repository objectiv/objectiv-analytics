/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { makeIdFromString } from '@objectiv/tracker-core';
import { OverlayContextWrapper, trackVisibility, useLocationStack, useOnChange } from '@objectiv/tracker-react-core';
import React, { useState } from 'react';
import { TrackedShowableContextProps } from '../types';

/**
 * Generates a new React Element already wrapped in an OverlayContext.
 * Automatically tracks HiddenEvent and VisibleEvent based on the given `isVisible` prop.
 */
export const TrackedOverlayContext = React.forwardRef<HTMLElement, TrackedShowableContextProps>((props, ref) => {
  const [wasVisible, setWasVisible] = useState<boolean>(false);
  const { id, Component, forwardId = false, isVisible = false, normalizeId = true, ...otherProps } = props;
  const locationStack = useLocationStack();

  let overlayId: string | null = id;
  if (normalizeId) {
    overlayId = makeIdFromString(overlayId);
  }

  useOnChange(isVisible, () => setWasVisible(isVisible));

  const componentProps = {
    ...otherProps,
    ...(ref ? { ref } : {}),
    ...(forwardId ? { id } : {}),
  };

  if (!overlayId) {
    if (globalThis.objectiv) {
      const locationPath = globalThis.objectiv.getLocationPath(locationStack);
      globalThis.objectiv.TrackerConsole.error(
        `｢objectiv｣ Could not generate a valid id for OverlayContext @ ${locationPath}. Please provide the \`id\` property.`
      );
    }
    return React.createElement(Component, componentProps);
  }

  return (
    <OverlayContextWrapper id={overlayId}>
      {(trackingContext) => {
        if ((wasVisible && !isVisible) || (!wasVisible && isVisible)) {
          trackVisibility({ isVisible, ...trackingContext });
        }
        return React.createElement(Component, componentProps);
      }}
    </OverlayContextWrapper>
  );
});
