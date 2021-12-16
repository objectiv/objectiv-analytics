/*
 * Copyright 2021 Objectiv B.V.
 */

import { useLocationStack } from './useLocationStack';

/**
 * A utility hook to retrieve the parent LocationContext. Returns `null` if none is found.
 */
export const useParentLocationContext = () => {
  const locationStack = useLocationStack();
  const [parentLocationContext] = locationStack.reverse();

  return parentLocationContext;
};
