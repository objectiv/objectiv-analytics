/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { isAbstractContext, isContextEqual, makePressableContext } from '../src';

describe('isContextEqual', () => {
  it(`should return false: wrong inputs`, () => {
    const context = makePressableContext({ id: 'pressable-id' });
    const nonExistingContext = { ...context, _type: 'InvalidContextName' };
    expect(isAbstractContext(context)).toBe(true);
    const wrongInputCases = [
      [undefined, undefined],
      [undefined, context],
      [context, undefined],
      [null, null],
      [null, context],
      [context, null],
      [{}, {}],
      [{}, context],
      [context, {}],
      [[], []],
      [[], context],
      [context, []],
      [nonExistingContext, nonExistingContext],
      [nonExistingContext, context],
      [context, nonExistingContext],
    ];

    wrongInputCases.forEach(([a, b]) => {
      // @ts-ignore silence TS on wrong input
      expect(isContextEqual(a, b)).toBe(false);
    });
  });

  it(`should return false: attribute count mismatch`, () => {
    const contextA = makePressableContext({ id: 'pressable-id' });
    const contextB = makePressableContext({ id: 'pressable-id' });
    const mutatedContextA = { ...contextA, customAttributeA: 1 };
    expect(isContextEqual(mutatedContextA, contextB)).toBe(false);
    expect(isContextEqual(contextB, mutatedContextA)).toBe(false);
  });

  it(`should return false: attribute name mismatch`, () => {
    const contextA = makePressableContext({ id: 'pressable-id' });
    const contextB = makePressableContext({ id: 'pressable-id' });
    const mutatedContextA = { ...contextA, customAttributeA: 1 };
    const mutatedContextB = { ...contextB, customAttributeB: 1 };
    expect(isContextEqual(mutatedContextA, mutatedContextB)).toBe(false);
    expect(isContextEqual(mutatedContextB, mutatedContextA)).toBe(false);
  });

  it(`should return false: attribute value mismatch`, () => {
    const contextA = makePressableContext({ id: 'pressable-id' });
    const contextB = makePressableContext({ id: 'pressable-id' });
    const mutatedContextA = { ...contextA, customAttribute: 1 };
    const mutatedContextB = { ...contextB, customAttribute: 2 };
    expect(isContextEqual(mutatedContextA, mutatedContextB)).toBe(false);
    expect(isContextEqual(mutatedContextB, mutatedContextA)).toBe(false);
  });

  it(`should return true: different instances of identical contexts`, () => {
    const contextA = makePressableContext({ id: 'pressable-id' });
    const contextB = makePressableContext({ id: 'pressable-id' });
    expect(isContextEqual(contextA, contextB)).toBe(true);
  });
});
