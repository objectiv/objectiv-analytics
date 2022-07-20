/*
 * Copyright 2022 Objectiv B.V.
 */

import { AbstractContext } from '@objectiv/schema';
import { ContextNames } from './ContextNames';

/**
 * A type guard to determine if the given object has the shape of an AbstractContext.
 */
export const isAbstractContext = (context: AbstractContext): context is AbstractContext => {
  // Type check
  if (typeof context !== 'object' || context === null || context === undefined) {
    return false;
  }

  // Attributes check
  if (!context._type || !context.id) {
    return false;
  }

  // _type attribute check
  return ContextNames.has(context._type);
};
