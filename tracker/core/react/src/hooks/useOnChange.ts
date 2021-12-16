/*
 * Copyright 2021 Objectiv B.V.
 */

import { useEffect, useRef } from 'react';
import isEqual from 'fast-deep-equal/es6';
import { OnChangeEffectCallback } from '../types';

/**
 * A side effect that monitors the given `state` and runs the given `effect` when it changes.
 */
export const useOnChange = <T>(state: T, effect: OnChangeEffectCallback) => {
  let previousStateRef = useRef<T>(state);
  let latestEffectRef = useRef(effect);

  latestEffectRef.current = effect;

  useEffect(() => {
    if (!isEqual(previousStateRef.current, state)) {
      effect(previousStateRef.current, state);
      previousStateRef.current = state;
    }
  }, [state]);
};
