/*
 * Copyright 2022 Objectiv B.V.
 */

describe('index (cjs)', () => {
  it('Should create the objectiv global', async () => {
    expect(globalThis.objectiv).toBeUndefined();
    require('../src');
    expect(globalThis.objectiv.devTools).not.toBeUndefined();
  });
});
