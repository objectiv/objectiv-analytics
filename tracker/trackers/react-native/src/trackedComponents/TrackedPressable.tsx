/*
 * Copyright 2021 Objectiv B.V.
 */

import { makeIdFromString } from '@objectiv/tracker-core';
import {
  makeTitleFromChildren,
  PressableContextWrapper,
  trackPressEvent,
  useLocationStack,
} from '@objectiv/tracker-react-core';
import React from 'react';
import { PressableProps, Pressable } from 'react-native';

/**
 * TrackedPressable has the same props of Pressable with and additional required `id` prop.
 */
export type TrackedPressableProps = PressableProps & {
  /**
   * Optional. Auto-generated from `children`. Used to set a PressableContext `id` manually.
   */
  id?: string;
};

/**
 * A Pressable already wrapped in PressableContext automatically tracking PressEvent.
 */
export const TrackedPressable = (props: TrackedPressableProps) => {
  const { id, ...pressableProps } = props;

  // Either use the given id or attempt to auto-detect `id` for LinkContext by looking at the `children` prop.
  const title = makeTitleFromChildren(props.children);
  const contextId = id ?? makeIdFromString(title);

  // If we couldn't generate an `id`, log the issue and return an untracked Component.
  const locationStack = useLocationStack();
  if (!contextId) {
    if (globalThis.objectiv) {
      const locationPath = globalThis.objectiv.getLocationPath(locationStack);
      globalThis.objectiv.TrackerConsole.error(
        `｢objectiv｣ Could not generate a valid id for PressableContext @ ${locationPath}. Please provide the \`id\` property manually.`
      );
    }
    return <Pressable {...pressableProps} />;
  }

  return (
    <PressableContextWrapper id={contextId}>
      {(trackingContext) => (
        <Pressable
          {...pressableProps}
          onPress={(event) => {
            pressableProps.onPress && pressableProps.onPress(event);
            trackPressEvent(trackingContext);
          }}
        />
      )}
    </PressableContextWrapper>
  );
};
