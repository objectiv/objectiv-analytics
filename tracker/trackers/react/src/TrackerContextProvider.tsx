import { Tracker } from '@objectiv/tracker-core';
import { createContext, ReactNode, useContext } from 'react';

/**
 * Tracker Context has just one `tracker` property which holds a Tracker instance
 */
export const TrackerContext = createContext<Partial<{ tracker: Tracker }>>({});

/**
 * Retrieves a Tracker instance from the closest TrackerContext.Provider
 * Logs an error if no TrackerContextProvider has been wrapped around the using Component.
 */
export const useTracker = () => {
  const { tracker } = useContext(TrackerContext);

  if (!tracker) {
    throw new Error('Objectiv: `useTracker` requires `TrackerContextProvider` to be present in the Components tree.');
  }

  return tracker;
};

/**
 * TrackerContextProvider is used to wrap logical sections of the Application and assign a Tracker instance to them.
 *
 * Components can use the useTracker hook, or consume TrackerContext directly, to retrieve the closest parent
 * tracker instance in the Components tree.
 */
export const TrackerContextProvider = ({ tracker, children }: { tracker: Tracker; children: ReactNode }) => (
  <TrackerContext.Provider value={{ tracker }}>{children}</TrackerContext.Provider>
);
