/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { makeIdFromString } from '@objectiv/tracker-core';
import { MediaPlayerContextWrapper, useLocationStack } from '@objectiv/tracker-react-core';
import React from 'react';
import { TrackedContextProps } from '../types';

/**
 * Generates a new React Element already wrapped in a MediaPlayerContext.
 */
export const TrackedMediaPlayerContext = React.forwardRef<HTMLElement, TrackedContextProps>((props, ref) => {
  const { id, Component, forwardId = false, normalizeId = true, ...otherProps } = props;
  const locationStack = useLocationStack();

  let mediaPlayerId: string | null = id;
  if (normalizeId) {
    mediaPlayerId = makeIdFromString(mediaPlayerId);
  }

  const componentProps = {
    ...otherProps,
    ...(ref ? { ref } : {}),
    ...(forwardId ? { id } : {}),
  };

  if (!mediaPlayerId) {
    if (globalThis.objectiv) {
      const locationPath = globalThis.objectiv.getLocationPath(locationStack);
      globalThis.objectiv.TrackerConsole.error(
        `｢objectiv｣ Could not generate a valid id for MediaPlayerContext @ ${locationPath}. Please provide the \`id\` property.`
      );
    }
    return React.createElement(Component, componentProps);
  }

  return (
    <MediaPlayerContextWrapper id={mediaPlayerId}>
      {React.createElement(Component, componentProps)}
    </MediaPlayerContextWrapper>
  );
});
