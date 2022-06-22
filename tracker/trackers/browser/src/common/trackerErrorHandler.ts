/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { TrackerErrorHandlerCallback } from '../definitions/TrackerErrorHandlerCallback';

/**
 * Generic onError callback, parameter and error handler for tag and track functions.
 * Allows developers to provide an onError callback to handle errors themselves.
 * Default behavior is to TrackerConsole.error.
 */
export const trackerErrorHandler = (error: unknown, parameters?: unknown, onError?: TrackerErrorHandlerCallback) => {
  if (onError) {
    onError(error);
  } else {
    globalThis.objectiv.devTools?.TrackerConsole.error(error, parameters);
  }
  return undefined;
};
