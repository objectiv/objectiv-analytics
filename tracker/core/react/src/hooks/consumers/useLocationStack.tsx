/*
 * Copyright 2021 Objectiv B.V.
 */

import { useContext } from 'react';
import { LocationProviderContext } from '../../common/providers/LocationProviderContext';

/**
 * A utility hook to easily retrieve the LocationStack from the LocationProviderContext.
 */
export const useLocationStack = () => {
  const locationProviderContext = useContext(LocationProviderContext);

  if (!locationProviderContext) {
    throw new Error(`
      Couldn't get a LocationStack. 
      Is the Component in a ObjectivProvider, TrackingContextProvider or LocationProvider?
    `);
  }

  // Return a clone of the actual LocationStack to safeguard against mutations
  return [...locationProviderContext.locationStack];
};
