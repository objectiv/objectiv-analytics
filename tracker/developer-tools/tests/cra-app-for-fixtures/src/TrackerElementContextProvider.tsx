import { StackFrame } from '@objectiv/developer-tools';
import { createContext, Dispatch, ReactNode, SetStateAction, useContext, useState } from 'react';
import { TrackedElementMetadata } from './tracker';

type TrackerElementContextState = {
  stackTrace?: string;
  rawStackFrames?: StackFrame[];
  mappedStackFrames?: StackFrame[];
  elementMetadata?: TrackedElementMetadata;
};

export const TrackerElementContext = createContext<{
  elementContext: Partial<TrackerElementContextState>;
  setElementContext: Dispatch<SetStateAction<TrackerElementContextState>>;
}>({
  elementContext: {},
  setElementContext: () => {
    throw new Error('TrackerElementContext requires TrackerElementContextProvider');
  },
});

export const useElementContext = () => useContext(TrackerElementContext);

export const TrackerElementContextProvider = ({ children }: { children: ReactNode }) => {
  const [elementContext, setElementContext] = useState<Partial<TrackerElementContextState>>({});

  return (
    <TrackerElementContext.Provider value={{ elementContext, setElementContext }}>
      {children}
    </TrackerElementContext.Provider>
  );
};
