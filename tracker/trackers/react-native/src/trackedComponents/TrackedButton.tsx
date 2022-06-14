/*
 * Copyright 2022 Objectiv B.V.
 */

import { makeIdFromString } from '@objectiv/tracker-core';
import { PressableContextWrapper, trackPressEvent, useLocationStack } from '@objectiv/tracker-react-core';
import React from 'react';
import { Button, ButtonProps } from 'react-native';

/**
 * TrackedButton has the same props of Button with an additional optional `id` prop.
 */
export type TrackedButtonProps = ButtonProps & {
  /**
   * Optional. Auto-generated from `title`. Used to set a PressableContext `id` manually.
   */
  id?: string;
};

/**
 * A Button already wrapped in PressableContext automatically tracking PressEvent.
 */
export const TrackedButton = (props: TrackedButtonProps) => {
  const { id, ...buttonProps } = props;

  // Either use the given id or attempt to auto-detect `id` for LinkContext by looking at the `title` prop.
  const contextId = id ?? makeIdFromString(props.title);

  // If we couldn't generate an `id`, log the issue and return an untracked Component.
  const locationStack = useLocationStack();
  if (!contextId) {
    if (globalThis.objectiv) {
      const locationPath = globalThis.objectiv.getLocationPath(locationStack);
      globalThis.objectiv.TrackerConsole.error(
        `｢objectiv｣ Could not generate a valid id for PressableContext @ ${locationPath}. Please provide the \`id\` property manually.`
      );
    }
    return <Button {...buttonProps} />;
  }

  return (
    <PressableContextWrapper id={contextId}>
      {(trackingContext) => (
        <Button
          {...buttonProps}
          onPress={(event) => {
            trackPressEvent(trackingContext);
            props.onPress && props.onPress(event);
          }}
        />
      )}
    </PressableContextWrapper>
  );
};
