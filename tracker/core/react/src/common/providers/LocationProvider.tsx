/*
 * Copyright 2021 Objectiv B.V.
 */

import { ReactNode, useContext } from 'react';
import { LocationProviderContext } from './LocationProviderContext';

/**
 * The props of LocationProvider.
 */
export type LocationProviderProps = LocationProviderContext & {
  /**
   * LocationProvider children can also be a function (render props).
   */
  children: ReactNode | ((parameters: LocationProviderContext) => void);
};

/**
 * LocationProvider inherits the LocationStack from its parent LocationProvider and adds its own Location
 * Contexts to it, effectively extending the stack with one or more LocationEntries.
 */
export const LocationProvider = ({ children, locationStack }: LocationProviderProps) => {
  const locationProviderContext = useContext(LocationProviderContext);
  const existingLocationStack = locationProviderContext?.locationStack ?? [];
  const newLocationProviderContextState: LocationProviderContext = {
    locationStack: [...existingLocationStack, ...locationStack],
  };

  return (
    <LocationProviderContext.Provider value={newLocationProviderContextState}>
      {typeof children === 'function' ? children(newLocationProviderContextState) : children}
    </LocationProviderContext.Provider>
  );
};
