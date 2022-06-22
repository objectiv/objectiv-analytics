/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { useEffect, useRef } from 'react';
import { EffectDestructor } from '../types';

/**
 * A side effect that runs only once on unmount. Uses a ref instead of deps for compatibility with React 18.
 */
export const useOnUnmountOnce = (destructor: EffectDestructor) => {
  const didRun = useRef(false);
  const latestDestructorRef = useRef<Function | undefined>(destructor);

  latestDestructorRef.current = destructor;

  useEffect(
    () => () => {
      if (!didRun.current && latestDestructorRef.current) {
        didRun.current = true;

        latestDestructorRef.current();
      }
    },
    []
  );
};
