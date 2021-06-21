import { useEffect, useRef } from 'react';
import isEqual from 'fast-deep-equal';

/**
 * A custom generic EffectCallback that received the monitored `previousState` and `state` values
 */
export type OnChangeEffectCallback = <T>(previousState: T, state: T) => void;

/**
 * A side effect that monitors the given `state` and runs the given `effect` when it changes.
 */
export const useOnChange = <T = unknown>(state: T, effect: OnChangeEffectCallback) => {
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
