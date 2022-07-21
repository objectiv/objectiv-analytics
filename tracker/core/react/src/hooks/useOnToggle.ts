/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { useEffect, useRef } from 'react';
import { OnToggleEffectCallback } from '../types';

/**
 * Monitors a boolean variable, or a predicate, and runs the given `trueEffect` or
 * `falseEffect` depending on the state value.
 *
 * If `falseEffect` is omitted, `trueEffect` is used for both states.
 */
export const useOnToggle = (
  state: boolean | (() => boolean),
  trueEffect: OnToggleEffectCallback,
  maybeFalseEffect?: OnToggleEffectCallback
) => {
  const falseEffect = maybeFalseEffect ?? trueEffect;
  const stateValue = typeof state === 'function' ? state() : state;
  let previousStateRef = useRef<boolean>(stateValue);
  let latestTrueEffectRef = useRef(trueEffect);
  let latestFalseEffectRef = useRef(falseEffect);

  latestTrueEffectRef.current = trueEffect;
  latestFalseEffectRef.current = falseEffect;

  useEffect(() => {
    if (!previousStateRef.current && stateValue) {
      trueEffect(previousStateRef.current, stateValue);
      previousStateRef.current = stateValue;
    } else if (previousStateRef.current && !stateValue) {
      falseEffect(previousStateRef.current, stateValue);
      previousStateRef.current = stateValue;
    }
  }, [stateValue]);
};
