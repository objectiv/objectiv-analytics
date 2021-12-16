/*
 * Copyright 2021 Objectiv B.V.
 */

import { renderHook } from '@testing-library/react-hooks';
import { useOnToggle } from '../src';

describe('useOnToggle', () => {
  const initialState = false;
  const mockTrueEffectCallback = jest.fn();
  const mockFalseEffectCallback = jest.fn();

  beforeEach(() => {
    jest.resetAllMocks();
  });

  afterEach(() => {
    jest.resetAllMocks();
  });

  it('should not execute on mount', () => {
    renderHook((state) => useOnToggle(state, mockTrueEffectCallback, mockFalseEffectCallback), {
      initialProps: initialState,
    });

    expect(mockTrueEffectCallback).not.toHaveBeenCalled();
    expect(mockFalseEffectCallback).not.toHaveBeenCalled();
  });

  it('should not execute on unmount', () => {
    const { unmount } = renderHook((state) => useOnToggle(state, mockTrueEffectCallback, mockFalseEffectCallback), {
      initialProps: initialState,
    });

    unmount();

    expect(mockTrueEffectCallback).not.toHaveBeenCalled();
    expect(mockFalseEffectCallback).not.toHaveBeenCalled();
  });

  it('should not execute on re-render if the state did not change', () => {
    const { rerender } = renderHook((state) => useOnToggle(state, mockTrueEffectCallback, mockFalseEffectCallback), {
      initialProps: initialState,
    });

    rerender(initialState);
    rerender(initialState);
    rerender(initialState);

    expect(mockTrueEffectCallback).not.toHaveBeenCalled();
    expect(mockFalseEffectCallback).not.toHaveBeenCalled();
  });

  it('should execute the correct side effect callback on re-render each time state changes', () => {
    const newState1 = true;
    const newState2 = false;
    const { rerender } = renderHook((state) => useOnToggle(state, mockTrueEffectCallback, mockFalseEffectCallback), {
      initialProps: initialState,
    });

    rerender(newState1);
    rerender(newState1);
    rerender(newState1);

    expect(mockTrueEffectCallback).toHaveBeenCalledTimes(1);
    expect(mockTrueEffectCallback).toHaveBeenCalledWith(initialState, newState1);
    expect(mockFalseEffectCallback).not.toHaveBeenCalled();

    jest.resetAllMocks();

    rerender(newState2);
    rerender(newState2);
    rerender(newState2);

    expect(mockFalseEffectCallback).toHaveBeenCalledTimes(1);
    expect(mockFalseEffectCallback).toHaveBeenCalledWith(newState1, newState2);
    expect(mockTrueEffectCallback).not.toHaveBeenCalled();
  });

  it('should execute the latest version of the effect callbacks', () => {
    const newState1 = true;
    const newState2 = false;
    const mockTrueEffectCallback2 = jest.fn();
    const mockTrueEffectCallback3 = jest.fn();
    const mockTrueEffectCallback4 = jest.fn();
    const mockFalseEffectCallback2 = jest.fn();
    const mockFalseEffectCallback3 = jest.fn();
    const mockFalseEffectCallback4 = jest.fn();
    const { rerender } = renderHook(
      ({ state, trueEffect, falseEffect }) => useOnToggle(state, trueEffect, falseEffect),
      {
        initialProps: { state: initialState, trueEffect: mockTrueEffectCallback, falseEffect: mockFalseEffectCallback },
      }
    );

    rerender({ state: initialState, trueEffect: mockTrueEffectCallback2, falseEffect: mockFalseEffectCallback2 });

    expect(mockTrueEffectCallback2).not.toHaveBeenCalled();
    expect(mockTrueEffectCallback3).not.toHaveBeenCalled();
    expect(mockTrueEffectCallback4).not.toHaveBeenCalled();
    expect(mockFalseEffectCallback2).not.toHaveBeenCalled();
    expect(mockFalseEffectCallback3).not.toHaveBeenCalled();
    expect(mockFalseEffectCallback4).not.toHaveBeenCalled();

    jest.resetAllMocks();

    rerender({ state: newState1, trueEffect: mockTrueEffectCallback3, falseEffect: mockFalseEffectCallback3 });

    expect(mockTrueEffectCallback2).not.toHaveBeenCalled();
    expect(mockTrueEffectCallback3).toHaveBeenCalledTimes(1);
    expect(mockTrueEffectCallback3).toHaveBeenCalledWith(initialState, newState1);
    expect(mockTrueEffectCallback4).not.toHaveBeenCalled();
    expect(mockFalseEffectCallback2).not.toHaveBeenCalled();
    expect(mockFalseEffectCallback3).not.toHaveBeenCalled();
    expect(mockFalseEffectCallback4).not.toHaveBeenCalled();

    jest.resetAllMocks();

    rerender({ state: newState2, trueEffect: mockTrueEffectCallback4, falseEffect: mockFalseEffectCallback4 });

    expect(mockTrueEffectCallback2).not.toHaveBeenCalled();
    expect(mockTrueEffectCallback3).not.toHaveBeenCalled();
    expect(mockTrueEffectCallback4).not.toHaveBeenCalled();
    expect(mockFalseEffectCallback2).not.toHaveBeenCalled();
    expect(mockFalseEffectCallback3).not.toHaveBeenCalled();
    expect(mockFalseEffectCallback4).toHaveBeenCalledTimes(1);
    expect(mockFalseEffectCallback4).toHaveBeenCalledWith(newState1, newState2);
  });
});
