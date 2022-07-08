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
import { Switch, SwitchProps } from 'react-native';

/**
 * TrackedSwitch has the same props of Switch with the addition of a required `id` prop.
 */
export type TrackedSwitchProps = SwitchProps & {
  /**
   * The InputContext `id`.
   */
  id: string;

  /**
   * Optional. Whether to track the switch value as '0' or '1'. Default to false.
   * When enabled, an InputValueContext will be generated and pushed into the Global Contexts of the InputChangeEvent.
   */
  trackValue?: boolean;
};

/**
 * A Switch already wrapped in InputContext.
 */
export function TrackedSwitch(props: TrackedSwitchProps) {
  const { id, trackValue = false, ...switchProps } = props;

  return (
    <InputContextWrapper id={id}>
      {(trackingContext) => (
        <Switch
          {...switchProps}
          onValueChange={(value) => {
            let inputChangeEventTrackerParameters: InputChangeEventTrackerParameters = trackingContext;

            // Add InputValueContext if trackValue has been set
            if (id && trackValue) {
              inputChangeEventTrackerParameters = {
                ...inputChangeEventTrackerParameters,
                globalContexts: [makeInputValueContext({ id, value: value ? '1' : '0' })],
              };
            }

            trackInputChangeEvent(inputChangeEventTrackerParameters);
            props.onValueChange && props.onValueChange(value);
          }}
        />
      )}
    </InputContextWrapper>
  );
}
