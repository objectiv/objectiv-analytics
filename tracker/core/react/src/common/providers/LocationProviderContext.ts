/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { LocationStack } from '@objectiv/tracker-core';
import { createContext } from 'react';

/**
 * LocationProviderContext state holds a LocationStack of LocationContexts.
 */
export type LocationProviderContext = {
  /**
   * An array of AbstractLocationContext objects.
   */
  locationStack: LocationStack;
};

/**
 * A Context to retrieve a LocationStack.
 * Components may access Context state either via `useContext(LocationProviderContext)` or `useLocationStack()`.
 */
export const LocationProviderContext = createContext<null | LocationProviderContext>(null);
