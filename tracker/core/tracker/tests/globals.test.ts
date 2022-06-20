/*
 * Copyright 2021-2022 Objectiv B.V.
 */

describe('globals', () => {
  it('should extend existing globals', () => {
    globalThis.objectiv = {
      //@ts-ignore
      devTools: 'mock',
    };
    require('../src');
    expect(globalThis.objectiv.devTools).not.toBeUndefined();
    expect(globalThis.objectiv.TrackerRepository).not.toBeUndefined();
  });
});
