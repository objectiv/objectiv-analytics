/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import React, { ReactNode } from 'react';
import { TrackerProviderContext } from './TrackerProviderContext';

/**
 * The props of TrackerProvider.
 */
export type TrackerProviderProps = TrackerProviderContext & {
  /**
   * TrackerProvider children can also be a function (render props).
   */
  children: ReactNode | ((parameters: TrackerProviderContext) => void);
};

/**
 * TrackerProvider wraps its children with TrackerContext.Provider. It's meant to be used as
 * high as possible in the Component tree. Children gain access to both the Tracker and their LocationStack.
 *
 * All LocationWrappers and `useTrack*` hooks require to be wrapped in TrackerProvider to function.
 *
 * @see LocationStackProvider
 * @see ObjectivProvider
 */
export const TrackerProvider = ({ children, tracker }: TrackerProviderProps) => {
  if (globalThis.objectiv.devTools) {
    globalThis.objectiv.devTools.LocationTree.clear();
  }

  return (
    <TrackerProviderContext.Provider value={{ tracker }}>
      {typeof children === 'function' ? children({ tracker }) : children}
    </TrackerProviderContext.Provider>
  );
};
