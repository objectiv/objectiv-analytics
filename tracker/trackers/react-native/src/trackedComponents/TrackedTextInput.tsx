/*
 * Copyright 2022 Objectiv B.V.
 */

import { makeInputValueContext } from '@objectiv/tracker-core';
import {
  InputChangeEventTrackerParameters,
  InputContextWrapper,
  trackInputChangeEvent,
} from '@objectiv/tracker-react-core';
import React from 'react';
import { TextInput, TextInputProps } from 'react-native';

/**
 * TrackedTextInput has the same props of TextInput with the addition of a required `id` prop.
 */
export type TrackedTextInputProps = TextInputProps & {
  /**
   * The InputContext `id`.
   */
  id: string;

  /**
   * Optional. Whether to track the input value. Default to false.
   * When enabled, an InputValueContext will be generated and pushed into the Global Contexts of the InputChangeEvent.
   */
  trackValue?: boolean;
};

/**
 * A TextInput already wrapped in InputContext.
 */
export function TrackedTextInput(props: TrackedTextInputProps) {
  const { id, trackValue = false, ...switchProps } = props;

  return (
    <InputContextWrapper id={id}>
      {(trackingContext) => (
        <TextInput
          {...switchProps}
          onEndEditing={(event) => {
            let inputChangeEventTrackerParameters: InputChangeEventTrackerParameters = trackingContext;

            // Add InputValueContext if trackValue has been set
            if (id && trackValue && event.nativeEvent && event.nativeEvent.text) {
              inputChangeEventTrackerParameters = {
                ...inputChangeEventTrackerParameters,
                globalContexts: [makeInputValueContext({ id, value: event.nativeEvent.text })],
              };
            }

            trackInputChangeEvent(inputChangeEventTrackerParameters);
            props.onEndEditing && props.onEndEditing(event);
          }}
        />
      )}
    </InputContextWrapper>
  );
}
