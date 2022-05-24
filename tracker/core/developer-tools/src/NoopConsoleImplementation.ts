/*
 * Copyright 2022 Objectiv B.V.
 */

import { TrackerConsoleImplementation } from '@objectiv/tracker-core';

/**
 * NoopConsole is an empty implementation of TrackerConsole that doesn't do anything.
 * Its main purpose is to forcefully disable the Console during dev mode or testing.
 */
export const NoopConsoleImplementation: TrackerConsoleImplementation = {
  debug: () => {},
  error: () => {},
  group: () => {},
  groupCollapsed: () => {},
  groupEnd: () => {},
  info: () => {},
  log: () => {},
  warn: () => {},
};
