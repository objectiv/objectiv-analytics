import { StackFrame } from "@objectiv/developer-tools";
import { createContext, Dispatch, ReactNode, SetStateAction, useContext, useState } from 'react';

type PositionContextState = {
  stackTrace?: string,
  rawStackFrames?: StackFrame[],
  mappedStackFrames?: StackFrame[],
}

export const PositionContext = createContext<{
  position?: Partial<PositionContextState>,
  setPosition?: Dispatch<SetStateAction<PositionContextState>>
}>({});

export const usePositionContext = () => useContext(PositionContext);

export const PositionContextProvider = ({ children }: { children: ReactNode }) => {
  const [position, setPosition] = useState<Partial<PositionContextState>>({});

  return <PositionContext.Provider value={{ position, setPosition}}>{children}</PositionContext.Provider>
};
