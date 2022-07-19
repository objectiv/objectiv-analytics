/*
 * Copyright 2022 Objectiv B.V.
 */

import { AbstractContext } from '@objectiv/schema';
import { getObjectKeys } from './helpers';
import { isAbstractContext } from './isAbstractContext';

/**
 * A predicate to match a Context to another. The comparison purposely ignores instance identifiers.
 */
export const isContextEqual = (contextA: AbstractContext, contextB: AbstractContext) => {
  // Input check
  if (!isAbstractContext(contextA) || !isAbstractContext(contextB)) {
    return false;
  }

  // Discard __instance_id by destructuring it out, as it's always different by design
  const { __instance_id: _a, ...a } = contextA;
  const { __instance_id: _b, ...b } = contextB;

  // Gather context A keys and length, reused in multiple tests below
  const aKeys = getObjectKeys(a);
  const aLength = aKeys.length;

  // Check attributes count
  if (aLength !== getObjectKeys(b).length) {
    return false;
  }

  // Check attributes names
  for (let i = 0; i < aLength; i++) {
    if (!b.hasOwnProperty(aKeys[i])) {
      return false;
    }
  }

  // Check attributes values
  for (let i = 0; i < aLength; i++) {
    const aKey = aKeys[i];

    if (a[aKey] !== b[aKey]) {
      return false;
    }
  }

  return true;
};
