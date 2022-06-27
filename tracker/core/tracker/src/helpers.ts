/*
 * Copyright 2021-2022 Objectiv B.V.
 */

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
 * A client-only valid UUID v4 generator. Does not guarantee 100% uniqueness, but it's good enough for what we need.
 *
 * The random string we use for building the UUID is composed by:
 *
 * 1. Current timestamp converted to hex string.
 *
 * 2. Math.random() converted to hex string. Note that:
 *   - It can return numbers ending with one or more 0s, thus .toString(16) will generate variable length strings.
 *   - It can return 0, which results in .toString(16) to simply return '0'.
 *
 * 3. We add 16 padding zeros at the end to compensate for Math.random() generating variable length strings.
 *   - We could make this yet another random string, but the edge case is so rare that I don't think it's worth it.
 *
 * Example of worst edge case, where Math.random() returns a 0:
 *
 *  rng = Date.now().toString(16) + '0' + '0'.repeat(16);
 *  > 181a434e63b00000000000000000
 *
 *  Would result in a UUID like this:
 *  > 181a434e-63b0-4000-8000-000000000000
 *
 *  Still more than fine for our use-case.
 */
export const generateUUID = () => {
  const rng = Date.now().toString(16) + Math.random().toString(16) + '0'.repeat(16);
  return [rng.substring(0, 8), rng.substring(8, 12), '4000-8' + rng.substring(13, 16), rng.substring(16, 28)].join('-');
};

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
