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
import { TouchableNativeFeedback, TouchableNativeFeedbackProps } from 'react-native';

/**
 * TrackedTouchableNativeFeedback has the same props of TouchableNativeFeedback with an additional required `id` prop.
 */
export type TrackedTouchableNativeFeedbackProps = TouchableNativeFeedbackProps & {
  /**
   * Optional. Auto-generated from `children`. Used to set a PressableContext `id` manually.
   */
  id?: string;
};

/**
 * A TouchableNativeFeedback already wrapped in PressableContext automatically tracking PressEvent.
 */
export const TrackedTouchableNativeFeedback = (props: TrackedTouchableNativeFeedbackProps) => {
  const { id, ...trackedTouchableNativeFeedbackProps } = props;

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
    return <TouchableNativeFeedback {...trackedTouchableNativeFeedbackProps} />;
  }

  return (
    <PressableContextWrapper id={contextId}>
      {(trackingContext) => (
        <TouchableNativeFeedback
          {...trackedTouchableNativeFeedbackProps}
          onPress={(event) => {
            trackedTouchableNativeFeedbackProps.onPress && trackedTouchableNativeFeedbackProps.onPress(event);
            trackPressEvent(trackingContext);
          }}
        />
      )}
    </PressableContextWrapper>
  );
};
