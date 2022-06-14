/*
 * Copyright 2022 Objectiv B.V.
 */

import { TrackerConsoleImplementation, TrackerConsoleInterface } from '@objectiv/tracker-core';
import { NoopConsoleImplementation } from './NoopConsoleImplementation';

/**
 * The default implementation of TrackerConsole. A singleton used pretty much by all other interfaces.
 */
export const TrackerConsole: TrackerConsoleInterface = {
  implementation: typeof window !== 'undefined' ? console : NoopConsoleImplementation,
  setImplementation: (implementation: TrackerConsoleImplementation) => (TrackerConsole.implementation = implementation),
  debug: (...args: any[]) => TrackerConsole.implementation.debug(...args),
  error: (...args: any[]) => TrackerConsole.implementation.error(...args),
  group: (...args: any[]) => TrackerConsole.implementation.group(...args),
  groupCollapsed: (...args: any[]) => TrackerConsole.implementation.groupCollapsed(...args),
  groupEnd: () => TrackerConsole.implementation.groupEnd(),
  info: (...args: any[]) => TrackerConsole.implementation.info(...args),
  log: (...args: any[]) => TrackerConsole.implementation.log(...args),
  warn: (...args: any[]) => TrackerConsole.implementation.warn(...args),
};
