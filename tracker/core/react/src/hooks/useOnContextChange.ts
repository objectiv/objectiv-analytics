/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { AbstractContext } from '@objectiv/schema';
import { isContextEqual } from '@objectiv/tracker-core';
import { useEffect, useRef } from 'react';
import { OnChangeEffectCallback } from '../types';

/**
 * A side effect that monitors the given `context` and runs the given `effect` when it changes.
 */
export const useOnContextChange = <T extends AbstractContext>(context: T, effect: OnChangeEffectCallback<T>) => {
  let previousStateRef = useRef<T>(context);
  let latestEffectRef = useRef(effect);

  latestEffectRef.current = effect;

  useEffect(() => {
    if (!isContextEqual(previousStateRef.current, context)) {
      effect(previousStateRef.current, context);
      previousStateRef.current = context;
    }
  }, [context]);
};
