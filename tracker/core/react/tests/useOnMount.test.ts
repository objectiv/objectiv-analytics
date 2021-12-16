/*
 * Copyright 2021 Objectiv B.V.
 */

import { renderHook } from '@testing-library/react-hooks';
import { useOnMount } from '../src';

describe('useOnMount', () => {
  const mockEffectCallback = jest.fn();

  beforeEach(() => {
    jest.resetAllMocks();
  });

  afterEach(() => {
    jest.resetAllMocks();
  });

  it('should execute once on mount', () => {
    renderHook(() => useOnMount(mockEffectCallback));

    expect(mockEffectCallback).toHaveBeenCalledTimes(1);
  });

  it('should not execute on unmount', () => {
    const { unmount } = renderHook(() => useOnMount(mockEffectCallback));

    expect(mockEffectCallback).toHaveBeenCalledTimes(1);

    unmount();

    expect(mockEffectCallback).toHaveBeenCalledTimes(1);
  });

  it('should not execute on rerender', () => {
    const { rerender } = renderHook(() => useOnMount(mockEffectCallback));

    expect(mockEffectCallback).toHaveBeenCalledTimes(1);

    rerender();
    rerender();
    rerender();

    expect(mockEffectCallback).toHaveBeenCalledTimes(1);
  });
});
