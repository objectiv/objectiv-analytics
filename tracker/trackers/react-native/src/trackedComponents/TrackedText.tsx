/*
 * Copyright 2022 Objectiv B.V.
 */

import { makeIdFromString } from '@objectiv/tracker-core';
import {
  makeTitleFromChildren,
  PressableContextWrapper,
  trackPressEvent,
  useLocationStack,
} from '@objectiv/tracker-react-core';
import React from 'react';
import { Text, TextProps } from 'react-native';

/**
 * TrackedText has the same props of Text with an additional optional `id` prop.
 */
export type TrackedTextProps = TextProps & {
  /**
   * Optional. Auto-generated from `children`. Used to set a PressableContext `id` manually.
   */
  id?: string;
};

/**
 * A Text already wrapped in PressableContext automatically tracking PressEvent.
 */
export const TrackedText = (props: TrackedTextProps) => {
  const { id, ...textProps } = props;

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
    return <Text {...textProps} />;
  }

  return (
    <PressableContextWrapper id={contextId}>
      {(trackingContext) => (
        <Text
          {...textProps}
          onPress={(event) => {
            trackPressEvent(trackingContext);
            props.onPress && props.onPress(event);
          }}
        />
      )}
    </PressableContextWrapper>
  );
};
