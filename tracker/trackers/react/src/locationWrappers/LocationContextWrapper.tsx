/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { AbstractLocationContext } from '@objectiv/schema';
import React, { ReactNode } from 'react';
import { LocationTree } from '../common/LocationTree';
import { LocationProvider } from '../common/providers/LocationProvider';
import { TrackingContext } from '../common/providers/TrackingContext';
import { useParentLocationContext } from '../hooks/consumers/useParentLocationContext';
import { useTracker } from '../hooks/consumers/useTracker';
import { useOnChange } from '../hooks/useOnChange';
import { useOnMount } from '../hooks/useOnMount';
import { useOnUnmount } from '../hooks/useOnUnmount';
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
  const parentLocationContext = useParentLocationContext();

  useOnMount(() => {
    LocationTree.add(locationContext, parentLocationContext);
  });

  useOnUnmount(() => {
    LocationTree.remove(locationContext);
  });

  useOnChange<LocationContext<AbstractLocationContext>>(locationContext, (previousLocationContext) => {
    LocationTree.remove(previousLocationContext);
    LocationTree.add(locationContext, parentLocationContext);
  });

  return (
    <LocationProvider locationStack={[locationContext]}>
      {(locationProviderContextState) =>
        typeof children === 'function' ? children({ tracker, ...locationProviderContextState }) : children
      }
    </LocationProvider>
  );
};
