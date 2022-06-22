/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { EffectCallback, useEffect, useRef } from 'react';

/**
 * A side effect that runs once on mount. Uses a ref instead of deps for compatibility with React 18.
 */
export const useOnMountOnce = (effect: EffectCallback) => {
  const didRun = useRef(false);

  useEffect(() => {
    if (!didRun.current) {
      didRun.current = true;

      effect();
    }
  }, []);
};
