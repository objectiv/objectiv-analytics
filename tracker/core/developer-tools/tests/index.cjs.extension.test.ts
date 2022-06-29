/*
 * Copyright 2022 Objectiv B.V.
 */

describe('index (cjs - extension)', () => {
  it('Should extend the objectiv global', async () => {
    expect(globalThis.objectiv).toBeUndefined();
    // @ts-ignore
    globalThis.objectiv = { someOtherGlobal: 'value' };
    require('../src');
    // @ts-ignore
    expect(globalThis.objectiv.someOtherGlobal).toBe('value');
    expect(globalThis.objectiv.devTools).not.toBeUndefined();
  });
});
