/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { makeHiddenEvent, Tracker } from '@objectiv/tracker-core';
import { render } from '@testing-library/react';
import { renderHook } from '@testing-library/react-hooks';
import React from 'react';
import { useEffect } from 'react';
import { TrackerProvider, useTrackOnUnmount } from '../src';

describe('useTrackOnUnmount', () => {
  beforeEach(() => {
    jest.resetAllMocks();
  });

  afterEach(() => {
    jest.resetAllMocks();
  });

  const LogTransport = { transportName: 'LogTransport', handle: jest.fn(), isUsable: () => true };
  const renderSpy = jest.fn();
  const tracker = new Tracker({ applicationId: 'app-id', transport: LogTransport });

  const Index = () => {
    return (
      <TrackerProvider tracker={tracker}>
        <Application />
      </TrackerProvider>
    );
  };

  const Application = () => {
    useTrackOnUnmount({ event: makeHiddenEvent() });

    useEffect(renderSpy);

    return <>Test application</>;
  };

  it('should not execute on mount', () => {
    render(<Index />);

    expect(LogTransport.handle).not.toHaveBeenCalled();
  });

  it('should execute on unmount', () => {
    const { unmount } = render(<Index />);

    unmount();

    expect(LogTransport.handle).toHaveBeenCalledTimes(1);
    expect(LogTransport.handle).toHaveBeenCalledWith(expect.objectContaining({ _type: 'HiddenEvent' }));
  });

  it('should not execute on rerender', () => {
    const { rerender } = render(<Index />);

    rerender(<Index />);
    rerender(<Index />);

    expect(renderSpy).toHaveBeenCalledTimes(3);
    expect(LogTransport.handle).not.toHaveBeenCalled();
  });

  it('should allow overriding the tracker with a custom one', () => {
    const LogTransport2 = {
      transportName: 'LogTransport2',
      handle: jest.fn(),
      isUsable: () => true,
    };
    const anotherTracker = new Tracker({ applicationId: 'app-id', transport: LogTransport2 });
    const { unmount } = renderHook(() => useTrackOnUnmount({ event: makeHiddenEvent(), tracker: anotherTracker }));

    unmount();

    expect(LogTransport.handle).not.toHaveBeenCalled();
    expect(LogTransport2.handle).toHaveBeenCalledTimes(1);
    expect(LogTransport2.handle).toHaveBeenCalledWith(expect.objectContaining({ _type: 'HiddenEvent' }));
  });
});
