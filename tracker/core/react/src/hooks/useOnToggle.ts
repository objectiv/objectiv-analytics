/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { useEffect, useRef } from 'react';
import { OnToggleEffectCallback } from '../types';

/**
 * A variant of the onChange side effect that monitors a boolean `state` and runs the given `trueEffect` or
 * `falseEffect` depending on the state value.
 */
export const useOnToggle = (
  state: boolean,
  trueEffect: OnToggleEffectCallback,
  falseEffect: OnToggleEffectCallback
) => {
  let previousStateRef = useRef<boolean>(state);
  let latestTrueEffectRef = useRef(trueEffect);
  let latestFalseEffectRef = useRef(falseEffect);

  latestTrueEffectRef.current = trueEffect;
  latestFalseEffectRef.current = falseEffect;

  useEffect(() => {
    if (!previousStateRef.current && state) {
      trueEffect(previousStateRef.current, state);
      previousStateRef.current = state;
    } else if (previousStateRef.current && !state) {
      falseEffect(previousStateRef.current, state);
      previousStateRef.current = state;
    }
  }, [state]);
};
