/*
 * Copyright 2022 Objectiv B.V.
 */

import { uuidv4 } from "@objectiv/tracker-core";

describe('uuidv4', () => {
  jest.spyOn(uuidv4, 'uuidv4_Crypto_RandomUUID');
  jest.spyOn(uuidv4, 'uuidv4_Crypto_GetRandomValues');
  jest.spyOn(uuidv4, 'uuidv4_DateNow_MathRandom');

  beforeEach(()=>{
    jest.resetAllMocks();
  })

  afterAll(()=>{
    jest.restoreAllMocks();
  })

  it('should invoke uuidv4_DateNow_MathRandom when `crypto` is not available', function () {
    // @ts-ignore
    globalThis.crypto = undefined;
    expect(globalThis.crypto).toBeUndefined();
    uuidv4();
    expect(uuidv4.uuidv4_DateNow_MathRandom).toHaveBeenCalled();
  });

  it('should invoke uuidv4_Crypto_GetRandomValues when `crypto` is available but `randomUUID` is not ', function () {
    // @ts-ignore
    globalThis.crypto = {
      getRandomValues: jest.fn()
    };
    expect(globalThis.crypto).not.toBeUndefined();
    expect(globalThis.crypto.randomUUID).toBeUndefined();
    expect(globalThis.crypto.getRandomValues).not.toBeUndefined();
    uuidv4();
    expect(uuidv4.uuidv4_Crypto_GetRandomValues).toHaveBeenCalled();
  });

  it('should invoke uuidv4_Crypto_RandomUUID when `crypto` and its `randomUUID` method are available', function () {
    // @ts-ignore
    globalThis.crypto = {
      randomUUID: jest.fn()
    };
    expect(globalThis.crypto).not.toBeUndefined();
    expect(globalThis.crypto.randomUUID).not.toBeUndefined();
    expect(uuidv4.uuidv4_Crypto_RandomUUID).not.toHaveBeenCalled();
    uuidv4();
    expect(uuidv4.uuidv4_Crypto_RandomUUID).toHaveBeenCalled();
  });
});

describe('uuidv4.uuidv4_Crypto_RandomUUID', () => {
  it('should invoke `crypto.randomUUID`', function () {
    // @ts-ignore
    globalThis.crypto = {
      randomUUID: jest.fn()
    };
    expect(globalThis.crypto.randomUUID).not.toHaveBeenCalled();
    uuidv4.uuidv4_Crypto_RandomUUID();
    expect(globalThis.crypto.randomUUID).toHaveBeenCalled();
  })
})

describe('uuidv4.uuidv4_Crypto_GetRandomValues', () => {
  it('should invoke `crypto.getRandomValues` 14 times', function () {
    // @ts-ignore
    globalThis.crypto = {
      // @ts-ignore
      getRandomValues: jest.fn(() => new Uint8Array(1))
    };
    expect(globalThis.crypto.getRandomValues).not.toHaveBeenCalled();
    uuidv4.uuidv4_Crypto_GetRandomValues();
    expect(globalThis.crypto.getRandomValues).toHaveBeenCalledTimes(31); // not 32, because one digit is always `4`
  })
})

describe('uuidv4.uuidv4_DateNow_MathRandom', () => {
  const originalDateNow = Date.now.bind(globalThis.Date);
  const originalMathRandom = Math.random.bind(globalThis.Math);

  beforeAll(() => {
    globalThis.Date.now = jest.fn(() => 1530518207007);
    globalThis.Math.random = jest.fn(() => 0.5);
  })

  afterAll(() => {
    global.Date.now = originalDateNow;
    global.Math.random = originalMathRandom;
  })

  it('should invoke `Date.now()` and `Math.random()`', function () {
    // @ts-ignore
    globalThis.crypto = undefined;
    expect(Date.now).not.toHaveBeenCalled();
    expect(Math.random).not.toHaveBeenCalled();
    uuidv4.uuidv4_DateNow_MathRandom();
    expect(Date.now).toHaveBeenCalled();
    expect(Math.random).toHaveBeenCalled();
  })
})
