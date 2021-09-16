/**
 * Generic onError callback, parameter and error handler for track functions.
 * Allows developers to provide an onError callback to handle errors themselves.
 * Default behavior is to console.error.
 */
export type TrackOnErrorCallback = <T = unknown>(error: unknown, parameters?: T) => void;

export const trackerErrorHandler = (error: unknown, parameters?: unknown, onError?: TrackOnErrorCallback) => {
  if (onError) {
    onError(error);
  } else {
    console.error(error, parameters);
  }
  return undefined;
};
