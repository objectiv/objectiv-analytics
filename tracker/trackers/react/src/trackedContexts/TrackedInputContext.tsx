/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { makeIdFromString } from '@objectiv/tracker-core';
import {
  InputContextWrapper,
  TrackingContext,
  trackInputChangeEvent,
  useLocationStack,
} from '@objectiv/tracker-react-core';
import React, { FocusEvent, useState } from 'react';
import { TrackedContextProps } from '../types';

/**
 * Generates a new React Element already wrapped in an InputContext.
 * Automatically tracks InputChangeEvent when the given Component receives an `onBlur` SyntheticEvent.
 */
export const TrackedInputContext = React.forwardRef<HTMLInputElement, TrackedContextProps<HTMLInputElement>>(
  (props, ref) => {
    const { id, Component, forwardId = false, defaultValue, normalizeId = true, ...otherProps } = props;
    const [previousValue, setPreviousValue] = useState<string>(defaultValue ? defaultValue.toString() : '');
    const locationStack = useLocationStack();

    let inputId: string | null = id;
    if (normalizeId) {
      inputId = makeIdFromString(inputId);
    }

    const handleBlur = async (event: FocusEvent<HTMLInputElement>, trackingContext: TrackingContext) => {
      if (previousValue !== event.target.value) {
        setPreviousValue(event.target.value);
        trackInputChangeEvent(trackingContext);
      }

      props.onBlur && props.onBlur(event);
    };

    const componentProps = {
      ...otherProps,
      ...(ref ? { ref } : {}),
      ...(forwardId ? { id } : {}),
      defaultValue,
    };

    if (!inputId) {
      if (globalThis.objectiv.devTools) {
        const locationPath = globalThis.objectiv.devTools.getLocationPath(locationStack);
        globalThis.objectiv.devTools.TrackerConsole.error(
          `｢objectiv｣ Could not generate a valid id for InputContext @ ${locationPath}. Please provide the \`id\` property.`
        );
      }
      return React.createElement(Component, componentProps);
    }

    return (
      <InputContextWrapper id={inputId}>
        {(trackingContext) =>
          React.createElement(Component, {
            ...componentProps,
            onBlur: (event) => handleBlur(event, trackingContext),
          })
        }
      </InputContextWrapper>
    );
  }
);
