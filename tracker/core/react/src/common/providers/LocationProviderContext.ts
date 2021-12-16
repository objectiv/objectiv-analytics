/*
 * Copyright 2021 Objectiv B.V.
 */

import { createContext } from 'react';
import { LocationStack } from '../../types';

/**
 * LocationProviderContext state holds a LocationStack of LocationContexts.
 */
export type LocationProviderContext = {
  /**
   * An array of LocationContext<AbstractLocationContext> objects.
   */
  locationStack: LocationStack;
};

/**
 * A Context to retrieve LocationEntries and LocationStack.
 * Components may access Context state either via `useContext(LocationProviderContext)` or `useLocationEntries()`
 * or `useLocationStack()`.
 */
export const LocationProviderContext = createContext<null | LocationProviderContext>(null);
