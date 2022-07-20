/*
 * Copyright 2022 Objectiv B.V.
 */

import { uuidv4 } from '../src/uuidv4';

describe('uuidv4', () => {
  jest.spyOn(uuidv4, 'crypto_RandomUUID');
  jest.spyOn(uuidv4, 'crypto_GetRandomValues');
  jest.spyOn(uuidv4, 'dateNow_MathRandom');

  beforeEach(() => {
    // @ts-ignore
    globalThis.crypto = undefined;
    jest.resetAllMocks();
  });

  afterAll(() => {
    jest.restoreAllMocks();
  });

  it('should invoke `dateNow_MathRandom` when `crypto` is not available', function () {
    // @ts-ignore
    globalThis.crypto = undefined;
    expect(globalThis.crypto).toBeUndefined();
    uuidv4();
    expect(uuidv4.dateNow_MathRandom).toHaveBeenCalled();
  });

  it('should invoke `crypto_GetRandomValues` when `crypto` is available but `randomUUID` is not ', function () {
    globalThis.crypto = {
      // @ts-ignore
      randomUUID: undefined,
      getRandomValues: jest.fn(),
    };
    expect(globalThis.crypto).not.toBeUndefined();
    expect(globalThis.crypto.randomUUID).toBeUndefined();
    expect(globalThis.crypto.getRandomValues).not.toBeUndefined();
    uuidv4();
    expect(uuidv4.crypto_GetRandomValues).toHaveBeenCalled();
  });

  it('should invoke `crypto_RandomUUID` when `crypto` and its `randomUUID` method are available', function () {
    // @ts-ignore
    globalThis.crypto = {
      randomUUID: jest.fn(),
    };
    expect(globalThis.crypto).not.toBeUndefined();
    expect(globalThis.crypto.randomUUID).not.toBeUndefined();
    expect(uuidv4.crypto_RandomUUID).not.toHaveBeenCalled();
    uuidv4();
    expect(uuidv4.crypto_RandomUUID).toHaveBeenCalled();
  });
});

describe('uuidv4.crypto_RandomUUID', () => {
  it('should invoke `crypto.randomUUID`', function () {
    // @ts-ignore
    globalThis.crypto = {
      randomUUID: jest.fn(),
    };
    expect(globalThis.crypto.randomUUID).not.toHaveBeenCalled();
    uuidv4.crypto_RandomUUID();
    expect(globalThis.crypto.randomUUID).toHaveBeenCalled();
  });
});

describe('uuidv4.crypto_GetRandomValues', () => {
  it('should invoke `crypto.getRandomValues` 31 times', function () {
    // @ts-ignore
    globalThis.crypto = {
      // @ts-ignore
      getRandomValues: jest.fn(() => new Uint8Array(1)),
    };
    expect(globalThis.crypto.getRandomValues).not.toHaveBeenCalled();
    uuidv4.crypto_GetRandomValues();
    expect(globalThis.crypto.getRandomValues).toHaveBeenCalledTimes(31); // not 32, because one digit is always `4`
  });
});

describe('uuidv4.dateNow_MathRandom', () => {
  const originalDateNow = Date.now.bind(globalThis.Date);
  const originalMathRandom = Math.random.bind(globalThis.Math);

  beforeAll(() => {
    globalThis.Date.now = jest.fn(() => 1530518207007);
    globalThis.Math.random = jest.fn(() => 0.5);
  });

  afterAll(() => {
    global.Date.now = originalDateNow;
    global.Math.random = originalMathRandom;
  });

  it('should invoke `Date.now()` and `Math.random()`', function () {
    // @ts-ignore
    globalThis.crypto = undefined;
    expect(Date.now).not.toHaveBeenCalled();
    expect(Math.random).not.toHaveBeenCalled();
    uuidv4.dateNow_MathRandom();
    expect(Date.now).toHaveBeenCalled();
    expect(Math.random).toHaveBeenCalled();
  });
});
