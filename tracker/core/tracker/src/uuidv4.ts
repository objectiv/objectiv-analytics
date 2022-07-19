/*
 * Copyright 2022 Objectiv B.V.
 */

/**
 * Generates a v4 UUID. Automatically picks the best available implementation:
 *  - `crypto` available, `randomUUID` available: `crypto_RandomUUID`.
 *  - `crypto` available, `randomUUID` not available, `getRandomValues` available: `crypto_GetRandomValues`.
 *  - `crypto` not available: `dateNow_MathRandom`.
 *
 * The different implementations are also callable individually:
 *  - uuidv4.crypto_RandomUUID()
 *  - uuidv4.crypto_GetRandomValues()
 *  - uuidv4.dateNow_MathRandom()
 */
export function uuidv4() {
  const crypto = globalThis.crypto;

  if (crypto) {
    //@ts-ignore silence TS warnings for older TS versions. E.g. Angular 9 SDK.
    if (typeof crypto.randomUUID === 'function') {
      return uuidv4.crypto_RandomUUID();
    }

    //@ts-ignore silence TS warnings for older TS versions.  E.g. Angular 9 SDK.
    if (typeof crypto.getRandomValues === 'function') {
      return uuidv4.crypto_GetRandomValues();
    }
  }

  return uuidv4.dateNow_MathRandom();
}

/**
 * The most basic implementation is an alias of `crypto.randomUUID`
 */
uuidv4.crypto_RandomUUID = () => {
  //@ts-ignore silence TS warnings for older TS versions (Angular 9 SDK.), we check availability in the method above.
  return globalThis.crypto.randomUUID();
};

/**
 * Kudos to Robert Kieffer (https://github.com/broofa), co-author of the uuid js module, for sharing this on SO.
 * Source:
 *  https://stackoverflow.com/a/2117523
 */
uuidv4.crypto_GetRandomValues = () => {
  return `${1e7}-${1e3}-${4e3}-${8e3}-${1e11}`.replace(/[018]/g, (character: string) => {
    const number = parseInt(character);
    return (number ^ (globalThis.crypto.getRandomValues(new Uint8Array(1))[0] & (15 >> (number / 4)))).toString(16);
  });
};

/**
 * A simplistic `Date.now()` & `Math.random()` based pseudo random UUID v4.
 * Math.random is not as bad as it used to be:
 *  https://v8.dev/blog/math-random
 */
uuidv4.dateNow_MathRandom = () => {
  const rng = Date.now().toString(16) + Math.random().toString(16) + '0'.repeat(16);
  return [rng.substring(0, 8), rng.substring(8, 12), '4000-8' + rng.substring(13, 16), rng.substring(16, 28)].join('-');
};
