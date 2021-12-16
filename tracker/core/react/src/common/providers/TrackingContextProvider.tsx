/*
 * Copyright 2021 Objectiv B.V.
 */

import { ReactNode } from 'react';
import { LocationProvider } from './LocationProvider';
import { LocationProviderContext } from './LocationProviderContext';
import { TrackerProvider } from './TrackerProvider';
import { TrackerProviderContext } from './TrackerProviderContext';
import { TrackingContext } from './TrackingContext';

/**
 * the props of TrackingContextProvider.
 */
export type TrackingContextProviderProps = TrackerProviderContext &
  Partial<LocationProviderContext> & {
    /**
     * TrackingContextProvider children can also be a function (render props).
     */
    children: ReactNode | ((parameters: TrackingContext) => void);
  };

/**
 * TrackingContextProvider wraps its children with TrackerProvider and LocationProvider.
 */
export const TrackingContextProvider = ({ children, tracker, locationStack = [] }: TrackingContextProviderProps) => (
  <TrackerProvider tracker={tracker}>
    <LocationProvider locationStack={locationStack}>
      {(locationProviderContextState) =>
        typeof children === 'function' ? children({ tracker, ...locationProviderContextState }) : children
      }
    </LocationProvider>
  </TrackerProvider>
);
