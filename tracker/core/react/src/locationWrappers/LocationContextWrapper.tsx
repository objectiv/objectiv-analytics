/*
 * Copyright 2021 Objectiv B.V.
 */

import { AbstractLocationContext } from '@objectiv/schema';
import { ReactNode } from 'react';
import { LocationTree } from '../common/LocationTree';
import { LocationProvider } from '../common/providers/LocationProvider';
import { TrackingContext } from '../common/providers/TrackingContext';
import { useParentLocationContext } from '../hooks/consumers/useParentLocationContext';
import { useTracker } from '../hooks/consumers/useTracker';
import { LocationContext } from '../types';

/**
 * The props of LocationContextWrapper.
 */
export type LocationContextWrapperProps = {
  /**
   * A LocationContext instance.
   */
  locationContext: LocationContext<AbstractLocationContext>;

  /**
   * LocationContextWrapper children can also be a function (render props). Provides the combined TrackingContext.
   */
  children: ReactNode | ((parameters: TrackingContext) => void);
};

/**
 * Wraps its children in the given LocationContext by factoring a new LocationEntry for the LocationProvider.
 * When used via render-props provides its children with LocationProviderContextState and TrackerState.
 */
export const LocationContextWrapper = ({ children, locationContext }: LocationContextWrapperProps) => {
  const tracker = useTracker();

  // Add new LocationEntry to LocationTree as well
  LocationTree.add(locationContext, useParentLocationContext());

  return (
    <LocationProvider locationStack={[locationContext]}>
      {(locationProviderContextState) =>
        typeof children === 'function' ? children({ tracker, ...locationProviderContextState }) : children
      }
    </LocationProvider>
  );
};
