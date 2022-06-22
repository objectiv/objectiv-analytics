/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import React, { ReactNode, useContext } from 'react';
import { trackApplicationLoadedEvent } from '../../eventTrackers/trackApplicationLoadedEvent';
import { useOnMountOnce } from '../../hooks/useOnMountOnce';
import { ObjectivProviderContext } from './ObjectivProviderContext';
import { TrackerProviderContext } from './TrackerProviderContext';
import { TrackingContext } from './TrackingContext';
import { TrackingContextProvider } from './TrackingContextProvider';

/**
 * ObjectivProvider options object can be used to customize whether and which events to automatically track.
 */
export type ObjectivProviderOptions = {
  trackApplicationLoaded: boolean;
};

/**
 * The default ObjectivProvider Options.
 */
export const objectivProviderDefaultOptions: ObjectivProviderOptions = {
  trackApplicationLoaded: true,
};

/**
 * The props of ObjectivProvider.
 */
export type ObjectivProviderProps = TrackerProviderContext & {
  /**
   * ObjectivProvider children can also be a function (render props).
   */
  children: ReactNode | ((parameters: TrackingContext) => ReactNode);

  /**
   * Optional. A partial ObjectivProviderOptions object to override the default options.
   */
  options?: Partial<ObjectivProviderOptions>;
};

/**
 * ObjectivProvider adds automating tracking of ApplicationLoadedEvent to TrackingContextProvider.
 */
export const ObjectivProvider = ({ children, tracker, options }: ObjectivProviderProps) => {
  const { trackApplicationLoaded } = { ...objectivProviderDefaultOptions, ...options };
  const objectivProviderPresent = useContext(ObjectivProviderContext);

  if (objectivProviderPresent) {
    console.error(`
      ｢objectiv｣ ObjectivProvider should not be nested and should be placed as high as possible in the Application. 
      To override Tracker and/or LocationStack, use TrackingContextProvider instead.
    `);
  }

  useOnMountOnce(() => {
    if (trackApplicationLoaded) {
      trackApplicationLoadedEvent({ tracker });
    }
  });

  return (
    <ObjectivProviderContext.Provider value={true}>
      <TrackingContextProvider tracker={tracker}>
        {(trackingContext) => (typeof children === 'function' ? children(trackingContext) : children)}
      </TrackingContextProvider>
    </ObjectivProviderContext.Provider>
  );
};
