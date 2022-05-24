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
import { TouchableWithoutFeedback, TouchableWithoutFeedbackProps } from 'react-native';

/**
 * TrackedTouchableWithoutFeedback has the same props of TouchableWithoutFeedback with an additional required `id` prop.
 */
export type TrackedTouchableWithoutFeedbackProps = TouchableWithoutFeedbackProps & {
  /**
   * Optional. Auto-generated from `children`. Used to set a PressableContext `id` manually.
   */
  id?: string;
};

/**
 * A TouchableWithoutFeedback already wrapped in PressableContext automatically tracking PressEvent.
 */
export const TrackedTouchableWithoutFeedback = (props: TrackedTouchableWithoutFeedbackProps) => {
  const { id, ...trackedTouchableWithoutFeedbackProps } = props;

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
    return <TouchableWithoutFeedback {...trackedTouchableWithoutFeedbackProps} />;
  }

  return (
    <PressableContextWrapper id={contextId}>
      {(trackingContext) => (
        <TouchableWithoutFeedback
          {...trackedTouchableWithoutFeedbackProps}
          onPress={(event) => {
            trackedTouchableWithoutFeedbackProps.onPress && trackedTouchableWithoutFeedbackProps.onPress(event);
            trackPressEvent(trackingContext);
          }}
        />
      )}
    </PressableContextWrapper>
  );
};
