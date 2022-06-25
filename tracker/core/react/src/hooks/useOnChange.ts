/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { useEffect, useRef } from 'react';
import { OnChangeEffectCallback } from '../types';

/**
 * A side effect that monitors the given `state` and runs the given `effect` when it changes.
 */
export const useOnChange = <T>(state: T, effect: OnChangeEffectCallback<T>) => {
  let previousStateRef = useRef<T>(state);
  let latestEffectRef = useRef(effect);

  latestEffectRef.current = effect;

  useEffect(() => {
    if (JSON.stringify(previousStateRef.current) !== JSON.stringify(state)) {
      effect(previousStateRef.current, state);
      previousStateRef.current = state;
    }
  }, [state]);
};
