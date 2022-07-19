/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { makePressableContext } from '@objectiv/tracker-core';
import { renderHook } from '@testing-library/react-hooks';
import { useOnContextChange } from '../src/';

describe('useOnContextChange', () => {
  const initialState = makePressableContext({ id: 'pressable-id' });
  const mockEffectCallback = jest.fn();

  beforeEach(() => {
    jest.resetAllMocks();
  });

  afterEach(() => {
    jest.resetAllMocks();
  });

  it('should not execute on mount', () => {
    renderHook((state) => useOnContextChange(state, mockEffectCallback), { initialProps: initialState });

    expect(mockEffectCallback).not.toHaveBeenCalled();
  });

  it('should not execute on unmount', () => {
    const { unmount } = renderHook((state) => useOnContextChange(state, mockEffectCallback), {
      initialProps: initialState,
    });

    unmount();

    expect(mockEffectCallback).not.toHaveBeenCalled();
  });

  it('should not execute on re-render if the state did not change', () => {
    const { rerender } = renderHook((state) => useOnContextChange(state, mockEffectCallback), {
      initialProps: initialState,
    });

    rerender(initialState);
    rerender(initialState);
    rerender(initialState);

    expect(mockEffectCallback).not.toHaveBeenCalled();
  });

  it('should not execute on re-render if the state is identical', () => {
    const newState = { ...initialState };
    const { rerender } = renderHook((state) => useOnContextChange(state, mockEffectCallback), {
      initialProps: initialState,
    });

    rerender(newState);
    rerender(newState);
    rerender(newState);

    expect(mockEffectCallback).not.toHaveBeenCalled();
  });

  it('should execute on re-render each time state changes', () => {
    const newState1 = makePressableContext({ id: 'pressable-id-2' });
    const newState2 = makePressableContext({ id: 'pressable-id-3' });
    const { rerender } = renderHook((state) => useOnContextChange(state, mockEffectCallback), {
      initialProps: initialState,
    });

    rerender(newState1);
    rerender(newState1);
    rerender(newState1);

    expect(mockEffectCallback).toHaveBeenCalledTimes(1);
    expect(mockEffectCallback).toHaveBeenCalledWith(initialState, newState1);

    rerender(newState2);
    rerender(newState2);
    rerender(newState2);

    expect(mockEffectCallback).toHaveBeenCalledTimes(2);
    expect(mockEffectCallback).toHaveBeenCalledWith(newState1, newState2);
  });

  it('should execute the latest version of the effect callback', () => {
    const newState = makePressableContext({ id: 'pressable-id-4' });
    const mockEffectCallback2 = jest.fn();
    const mockEffectCallback3 = jest.fn();
    const mockEffectCallback4 = jest.fn();
    const { rerender } = renderHook(({ state, effect }) => useOnContextChange(state, effect), {
      initialProps: { state: initialState, effect: mockEffectCallback },
    });

    rerender({ state: initialState, effect: mockEffectCallback2 });
    rerender({ state: initialState, effect: mockEffectCallback3 });
    rerender({ state: newState, effect: mockEffectCallback4 });

    expect(mockEffectCallback).not.toHaveBeenCalled();
    expect(mockEffectCallback2).not.toHaveBeenCalled();
    expect(mockEffectCallback3).not.toHaveBeenCalled();
    expect(mockEffectCallback4).toHaveBeenCalledTimes(1);
    expect(mockEffectCallback4).toHaveBeenCalledWith(initialState, newState);
  });
});
