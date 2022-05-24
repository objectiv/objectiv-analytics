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
import { TouchableHighlight, TouchableHighlightProps } from 'react-native';

/**
 * TrackedTouchableHighlight has the same props of TouchableHighlight with an additional required `id` prop.
 */
export type TrackedTouchableHighlightProps = TouchableHighlightProps & {
  /**
   * Optional. Auto-generated from `children`. Used to set a PressableContext `id` manually.
   */
  id?: string;
};

/**
 * A TouchableHighlight already wrapped in PressableContext automatically tracking PressEvent.
 */
export const TrackedTouchableHighlight = (props: TrackedTouchableHighlightProps) => {
  const { id, ...trackedTouchableHighlightProps } = props;

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
    return <TouchableHighlight {...trackedTouchableHighlightProps} />;
  }

  return (
    <PressableContextWrapper id={contextId}>
      {(trackingContext) => (
        <TouchableHighlight
          {...trackedTouchableHighlightProps}
          onPress={(event) => {
            trackedTouchableHighlightProps.onPress && trackedTouchableHighlightProps.onPress(event);
            trackPressEvent(trackingContext);
          }}
        />
      )}
    </PressableContextWrapper>
  );
};
