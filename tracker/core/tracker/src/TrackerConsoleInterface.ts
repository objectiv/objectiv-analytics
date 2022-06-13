/*
 * Copyright 2021-2022 Objectiv B.V.
 */

/**
 * A subset of the Console interface methods.
 */
export type TrackerConsoleImplementation = Pick<
  Console,
  'debug' | 'error' | 'group' | 'groupCollapsed' | 'groupEnd' | 'info' | 'log' | 'warn'
>;

/**
 * TrackerConsole is a simplified implementation of Console.
 */
export type TrackerConsoleInterface = TrackerConsoleImplementation & {
  implementation: TrackerConsoleImplementation;
  setImplementation: (implementation: TrackerConsoleImplementation) => void;
};
