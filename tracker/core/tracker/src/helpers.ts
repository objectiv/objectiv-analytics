/*
 * Copyright 2021-2022 Objectiv B.V.
 */
import { v4 as uuid } from 'uuid';

/**
 * A TypeScript friendly Object.keys
 */
export const getObjectKeys = Object.keys as <T extends object>(obj: T) => Array<keyof T>;

/**
 * A TypeScript generic describing an array with at least one item of the given Type
 */
export type NonEmptyArray<T> = [T, ...T[]];

/**
 * A TypeScript NonEmptyArray guard
 */
export function isNonEmptyArray<T>(array: T[]): array is NonEmptyArray<T> {
  return array.length > 0;
}

/**
 * A UUID v4 generator
 */
export const generateUUID = () => uuid();

/**
 * Executes the given predicate every `intervalMs` for a maximum of `timeoutMs`.
 * It resolves to `true` if predicated returns `true`. Resolves to false if `timeoutMs` is reached.
 */
export const waitForPromise = async ({
  predicate,
  intervalMs,
  timeoutMs,
}: {
  predicate: Function;
  intervalMs: number;
  timeoutMs: number;
}): Promise<boolean> => {
  // If predicate is already truthy we can resolve right away
  if (predicate()) {
    return true;
  }

  // We need to keep track of two timers, one for the state polling and one for the global timeout
  let timeoutTimer: ReturnType<typeof setTimeout>;
  let pollingTimer: ReturnType<typeof setTimeout>;

  // A promise that will resolve when `predicate` is truthy. It polls every `intervalMs`.
  const resolutionPromiseResolver = (resolve: Function) => {
    if (predicate()) {
      resolve(true);
    } else {
      clearTimeout(pollingTimer);
      pollingTimer = setTimeout(() => resolutionPromiseResolver(resolve), intervalMs);
    }
  };
  const resolutionPromise = new Promise<boolean>(resolutionPromiseResolver);

  // A promise that will resolve to false after its timeout reaches `intervalMs`.
  const timeoutPromise = new Promise<boolean>(
    (resolve) => (timeoutTimer = setTimeout(() => resolve(false), timeoutMs))
  );

  // Race resolutionPromise against the timeoutPromise. Either the predicate resolves first or we reject on timeout.
  return Promise.race<boolean>([timeoutPromise, resolutionPromise]).finally(() => {
    clearTimeout(pollingTimer);
    clearTimeout(timeoutTimer);
  });
};

/**
 * An index value validator. Accepts 0 and positive integers only.
 */
export const isValidIndex = (index: number) => Number.isInteger(index) && Number.isFinite(index) && index >= 0;

/**
 * Converts the given text to a standardized format to be used as identifier for Location Contexts.
 * This may be used, among others, to infer a valid identifier from the title / label of a Button.
 */
export const makeIdFromString = (sourceString: string): string | null => {
  let id = '';

  if (typeof sourceString === 'string') {
    id = sourceString
      // Convert to lowercase
      .toLowerCase()
      // Trim it
      .trim()
      // Replace spaces with dashes
      .replace(/[\s]+/g, '-')
      // Remove non-alphanumeric characters except dashes and underscores
      .replace(/[^a-zA-Z0-9_-]+/g, '')
      // Get rid of duplicated dashes
      .replace(/-+/g, '-')
      // Get rid of duplicated underscores
      .replace(/_+/g, '_')
      // Get rid of leading or trailing underscores and dashes
      .replace(/^([-_])*|([-_])*$/g, '')
      // Truncate to 64 chars
      .slice(0, 64);
  }

  // Catch empty strings and return null
  if (!id || !id.length) {
    return null;
  }

  // Return processed id
  return id;
};

/**
 * Helper function to determine if we are in test mode by checking the Node environment.
 */
export const isTestMode = () => process.env.NODE_ENV?.startsWith('test') ?? false;

/**
 * Helper function to determine if we are in development or test mode by checking the Node environment.
 */
export const isDevMode = () => (process.env.NODE_ENV?.startsWith('dev') ?? false) || isTestMode();

/**
 * Helper function to determine if we are in a browser - quite simplistically by checking the window object.
 */
export const isBrowser = () => typeof window !== 'undefined';
