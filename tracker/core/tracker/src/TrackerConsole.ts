/**
 * TrackerConsole is a simplified implementation of Console.
 */
export type TrackerConsole = Pick<
  Console,
  'debug' | 'error' | 'group' | 'groupCollapsed' | 'groupEnd' | 'info' | 'log' | 'warn'
>;

/**
 * NoopConsole is an empty implementation of TrackerConsole that doesn't do anything.
 * Its main purpose is to forcefully disable the Console during dev mode or testing.
 */
export const NoopConsole: TrackerConsole = {
  debug: () => {},
  error: () => {},
  group: () => {},
  groupCollapsed: () => {},
  groupEnd: () => {},
  info: () => {},
  log: () => {},
  warn: () => {},
};
