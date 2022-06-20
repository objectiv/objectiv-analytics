/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { makeIdFromString } from '@objectiv/tracker-core';
import {
  makeTitleFromChildren,
  PressableContextWrapper,
  trackPressEvent,
  useLocationStack,
} from '@objectiv/tracker-react-core';
import React from 'react';
import { TrackedPressableContextProps } from '../types';

/**
 * Generates a new React Element already wrapped in an PressableContext.
 * Automatically tracks PressEvent when the given Component receives an `onClick` SyntheticEvent.
 */
export const TrackedPressableContext = React.forwardRef<HTMLElement, TrackedPressableContextProps>((props, ref) => {
  const { Component, id, title, forwardId = false, forwardTitle = false, normalizeId = true, ...otherProps } = props;

  // Attempt to auto-detect `id` for LinkContext by looking at either the `title` or `children` props.
  const pressableTitle = title ?? makeTitleFromChildren(props.children);
  let pressableId: string | null = id ?? pressableTitle;
  if (normalizeId) {
    pressableId = makeIdFromString(pressableId);
  }

  // Prepare new Component props
  const componentProps = {
    ...otherProps,
    ...(ref ? { ref } : {}),
    ...(forwardId ? { id } : {}),
    ...(forwardTitle ? { title } : {}),
  };

  // If we couldn't generate an `id`, log the issue and return an untracked Component.
  const locationStack = useLocationStack();
  if (!pressableId) {
    if (globalThis.objectiv.devTools) {
      const locationPath = globalThis.objectiv.devTools.getLocationPath(locationStack);
      globalThis.objectiv.devTools.TrackerConsole.error(
        `｢objectiv｣ Could not generate a valid id for PressableContext @ ${locationPath}. Please provide either the \`title\` or the \`id\` property manually.`
      );
    }
    return React.createElement(Component, componentProps);
  }

  // Wrap Component in PressableContextWrapper
  return (
    <PressableContextWrapper id={pressableId}>
      {(trackingContext) =>
        React.createElement(Component, {
          ...componentProps,
          onClick: (event) => {
            // Track click as PressEvent
            trackPressEvent(trackingContext);

            // If present, execute also onClick prop
            props.onClick && props.onClick(event);
          },
        })
      }
    </PressableContextWrapper>
  );
});
