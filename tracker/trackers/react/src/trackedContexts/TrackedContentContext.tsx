/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { makeIdFromString } from '@objectiv/tracker-core';
import { ContentContextWrapper, useLocationStack } from '@objectiv/tracker-react-core';
import React from 'react';
import { TrackedContextProps } from '../types';

/**
 * Generates a new React Element already wrapped in a ContentContext.
 */
export const TrackedContentContext = React.forwardRef<HTMLElement, TrackedContextProps>((props, ref) => {
  const { id, Component, forwardId = false, normalizeId = true, ...otherProps } = props;
  const locationStack = useLocationStack();

  let contentId: string | null = id;
  if (normalizeId) {
    contentId = makeIdFromString(contentId);
  }

  const componentProps = {
    ...otherProps,
    ...(ref ? { ref } : {}),
    ...(forwardId ? { id } : {}),
  };

  if (!contentId) {
    if (globalThis.objectiv.devTools) {
      const locationPath = globalThis.objectiv.devTools.getLocationPath(locationStack);
      globalThis.objectiv.devTools.TrackerConsole.error(
        `｢objectiv｣ Could not generate a valid id for ContentContext @ ${locationPath}. Please provide the \`id\` property.`
      );
    }
    return React.createElement(Component, componentProps);
  }

  return <ContentContextWrapper id={contentId}>{React.createElement(Component, componentProps)}</ContentContextWrapper>;
});
