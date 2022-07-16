/*
 * Copyright 2022 Objectiv B.V.
 */

import { uuidv4 } from "@objectiv/tracker-core";

jest.spyOn(uuidv4, 'uuidv4_Crypto_RandomUUID')
jest.spyOn(uuidv4, 'uuidv4_Crypto_GetRandomValues')
jest.spyOn(uuidv4, 'uuidv4_DateNow_MathRandom')

describe('uuidv4', () => {
  beforeEach(()=>{
    jest.resetAllMocks();
  })

  it('should invoke uuidv4_DateNow_MathRandom when `crypto` is not available', function () {
    expect(globalThis.crypto).toBeUndefined();
    uuidv4();
    expect(uuidv4.uuidv4_DateNow_MathRandom).toHaveBeenCalled();
  });
});
