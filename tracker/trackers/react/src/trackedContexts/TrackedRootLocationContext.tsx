/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { makeIdFromString } from '@objectiv/tracker-core';
import { RootLocationContextWrapper } from '@objectiv/tracker-react-core';
import React from 'react';
import { TrackedContextProps } from '../types';

/**
 * Generates a new React Element already wrapped in a RootLocationContext.
 */
export const TrackedRootLocationContext = React.forwardRef<HTMLElement, TrackedContextProps>((props, ref) => {
  const { id, Component, forwardId = false, normalizeId = true, ...otherProps } = props;

  let rootId: string | null = id;
  if (normalizeId) {
    rootId = makeIdFromString(rootId);
  }

  const componentProps = {
    ...otherProps,
    ...(ref ? { ref } : {}),
    ...(forwardId ? { id } : {}),
  };

  if (!rootId) {
    if (globalThis.objectiv.devTools) {
      globalThis.objectiv.devTools.TrackerConsole.error(
        `｢objectiv｣ Could not generate a valid id for RootLocationContext. Please provide the \`id\` property.`
      );
    }
    return React.createElement(Component, componentProps);
  }

  return (
    <RootLocationContextWrapper id={rootId}>
      {React.createElement(Component, componentProps)}
    </RootLocationContextWrapper>
  );
});
