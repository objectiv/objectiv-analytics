/*
 * Copyright 2022 Objectiv B.V.
 */

describe('index (esm)', () => {
  it('Should have created the objectiv global', async () => {
    expect(globalThis.objectiv).toBeUndefined();
    require('../src/index');
    expect(globalThis.objectiv).not.toBeUndefined();
  });
});
