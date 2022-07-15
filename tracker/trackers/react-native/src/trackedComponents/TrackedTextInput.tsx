/*
 * Copyright 2022 Objectiv B.V.
 */

import { makeInputValueContext } from '@objectiv/tracker-core';
import { EventTrackerParameters, InputContextWrapper, trackInputChangeEvent } from '@objectiv/tracker-react-core';
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
            let eventTrackerParameters: EventTrackerParameters = trackingContext;

            // Add InputValueContext if trackValue has been set
            if (id && trackValue && event.nativeEvent && event.nativeEvent.text) {
              eventTrackerParameters = {
                ...eventTrackerParameters,
                globalContexts: [makeInputValueContext({ id, value: event.nativeEvent.text })],
              };
            }

            trackInputChangeEvent(eventTrackerParameters);
            props.onEndEditing && props.onEndEditing(event);
          }}
        />
      )}
    </InputContextWrapper>
  );
}
