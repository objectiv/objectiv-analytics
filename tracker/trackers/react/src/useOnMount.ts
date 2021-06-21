import { EffectCallback, useEffect } from 'react';

/**
 * A side effect that runs only once on mount.
 */
export const useOnMount = (effect: EffectCallback) => useEffect(effect, []);
